from streaming.app import app
from streaming.config import config
from streaming.imagecompare.api.models import ComparePages, Matches
import imagehash
from faust import web

# Topics
screenshot_topic = app.topic('screenshot-results')
compare = {'hashes':[]}

@app.task
async def populate_dhash():
    pipeline = [ {'$lookup': {
            'from': 'snapshots', 'let': { 'url': '$url' }, 'as': 'screenshots',
            'pipeline': [ { '$match': { '$expr': {'$eq': ['$url', '$$url'] } }  }, {'$limit': 1} ] } } ]
    compare_objects = ComparePages.objects().aggregate(*pipeline)
    compare['hashes'] = [{'url':compare['url'], 'tag':compare['tag'], 'score':compare['score'],
        'dhash':compare['screenshots'][0]['dhash']} for compare in compare_objects]
   

@app.agent(screenshot_topic)
async def screenshot_results(screenshots):
    async for screenshot in screenshots:
        for dhash in compare['hashes']:
            original_hash = imagehash.hex_to_hash(dhash['dhash'])
            new_hash = imagehash.hex_to_hash(screenshot['dhash'])
            dist = (original_hash - new_hash)
            if int((original_hash - new_hash)) < int(dhash['score']):
                matches_object = Matches.objects(url=screenshot['url']).update(add_to_set__tags=dhash['tag'])
                print('Hamming distance: {0}'.format(dist))
                print('Breached model for {0}'.format(dhash['url']))


# Screenshot execution blueprint
api_imagecompare = web.Blueprint('api_imagecompare')

@api_imagecompare.route('/refresh', name='api_imagecompare')
class APIScreenshot(web.View):
    async def get(self, request: web.Request) -> web.Response:
        try:
            await populate_dhash()
            return self.json({'result': 'success', 'message':'Refreshing hash lookups'})

        except Exception as err:
            return self.json({'result': 'failed', 'message':'Unable to refresh hash lookup'})

app.web.blueprints.add('/imagecompare/', api_imagecompare)





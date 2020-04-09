from streaming.app import app
from streaming.scraper.topics import monitoring_topic
from faust import web
import base64

# Screenshot execution blueprint
api_screenshot = web.Blueprint('api_scrape')

@api_screenshot.route('/screenshot', name='api_screenshot')
class APIScreenshot(web.View):
    async def post(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()
            await monitoring_topic.send(value={'url':payload['url']})
            return self.json({'result': 'success', 'message':'Creating screenshot for url'})

        except Exception as err:
            return self.json({'result': 'failed', 'message':'Unable to process screenshot request'})

app.web.blueprints.add('/scrape/', api_screenshot)


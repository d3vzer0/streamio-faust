from streaming.wordmatching.api.match import Match
from streaming.wordmatching.topics import matched_topic, confirmed_topic
from streaming.wordmatching.api.models import Matches, Snapshots
from streaming.app import app
from faust import web
import json
import base64

@app.agent(matched_topic)
async def matched_certs(matches):
    async for match in matches:
        url = '{0}://{1}'.format(match['proto'], match['value']).replace('*.', '')
        await Match(url).create('transparency', match['source'], match['input'], match['data'])

# Confirmation blueprint
api_confirm = web.Blueprint('api_confirm')

@api_confirm.route('/confirm', name='api_confirm')
class APIConfirm(web.View):
    async def post(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()
            first_match = json.loads(Matches.objects(url=payload['url']).first().to_json())
            first_screenshot = Snapshots.objects(url=payload['url']).first()
            if first_screenshot:
                snapshot_file = first_screenshot.screenshot.read()
                result = {'state': payload['state'], 'match': first_match, 'screenshot':base64.b64encode(snapshot_file)}
            else:
                result = {'state': payload['state'], 'match': first_match }
            await confirmed_topic.send(value=result)
            return self.json({'result': 'success', 'message':result})

        except Exception as err:
            return self.json({'result': 'failed', 'message':'Unable to process confirmation'})

app.web.blueprints.add('/matches/', api_confirm)


from streaming.scraper.api.screenshot import Screenshot
from streaming.scraper.api.snapshot import Snapshot
from streaming.scraper.api.models import Matches
from streaming.app import app
from streaming.config import config
from faust import web
import concurrent.futures
import base64

# Topics
matched_topic = app.topic('wordmatching-hits')
monitoring_topic = app.topic('monitoring-urls')
screenshot_topic = app.topic('screenshot-results')

@app.agent(matched_topic)
async def matched_certs(matches):
    # Temp disabled multiproc to find a better solution
    # with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
    async for match in matches:
        url = '{0}://{1}'.format(match['proto'], match['value']).replace('*.', '')
        screenshot = Screenshot(url).to_png()
        create_snapshot = Snapshot(url).create(screenshot)
        await screenshot_topic.send(value={'url':url, 'sha256':create_snapshot['sha256'],
            'dhash':create_snapshot['dhash'], 'screenshot':base64.b64encode(screenshot).decode()})
        # executor.submit(Screenshot(url).to_png())


@app.agent(monitoring_topic)
async def monitor_url(urls):
    # Temp disabled multiproc to find a better solution
    # with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
    async for url in urls:
        screenshot = Screenshot(url['url']).to_png()
        create_snapshot = Snapshot(url['url']).create(screenshot)
        await screenshot_topic.send(value={'url':url['url'], 'sha256':create_snapshot['sha256'],
            'dhash': create_snapshot['dhash'], 'screenshot':base64.b64encode(screenshot).decode()})
        # executor.submit(Screenshot(url['url']).to_png())

@app.timer(interval=900, on_leader=True)
async def get_enabled():
    enabled_urls = Matches.objects(enabled=True)
    for match in enabled_urls:
        await monitoring_topic.send(value={'url': match['url']})

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


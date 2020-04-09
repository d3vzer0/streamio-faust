from streaming.scraper.api.screenshot import Screenshot
from streaming.scraper.api.snapshot import Snapshot
from streaming.scraper.api.models import Matches
from streaming.scraper.topics import monitoring_topic, screenshot_topic
from streaming.app import app
import base64

@app.agent(monitoring_topic)
async def monitor_url(urls):
    # Temp disabled multiproc to find a better solution
    # with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
    async for url in urls:
        screenshot = Screenshot(url['url']).to_png()
        create_snapshot = Snapshot(url['url']).create(screenshot)
        await screenshot_topic.send(value={'url':url['url'], 'sha256':create_snapshot['sha256'],
            'dhash': create_snapshot['dhash'], 'screenshot':base64.b64encode(screenshot).decode()})



@app.timer(interval=900, on_leader=True)
async def get_enabled():
    enabled_urls = Matches.objects(enabled=True)
    for match in enabled_urls:
        await monitoring_topic.send(value={'url': match['url']})
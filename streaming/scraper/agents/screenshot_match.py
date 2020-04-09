from streaming.scraper.api.screenshot import Screenshot
from streaming.scraper.api.snapshot import Snapshot
from streaming.scraper.api.models import Matches
from streaming.scraper.topics import matched_topic, screenshot_topic
from streaming.app import app
import base64


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

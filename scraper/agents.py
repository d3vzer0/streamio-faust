from streaming.scraper.api.screenshot import Screenshot
from streaming.app import app
from streaming.config import config
import concurrent.futures

# Topics
matched_topic = app.topic('wordmatching-hits')

@app.agent(matched_topic)
async def matched_certs(matches):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        async for match in matches:
            url = '{0}://{1}'.format(match['proto'], match['value']).replace('*.', '')
            executor.submit(Screenshot(url).to_png())
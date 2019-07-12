from streaming.scraper.api.screenshot import Screenshot
from streaming.scraper.api.models import Matches

from streaming.app import app
from streaming.config import config
import concurrent.futures

# Topics
matched_topic = app.topic('wordmatching-hits')
monitoring_topic = app.topic('monitoring-urls')

@app.agent(matched_topic)
async def matched_certs(matches):
    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        async for match in matches:
            url = '{0}://{1}'.format(match['proto'], match['value']).replace('*.', '')
            executor.submit(Screenshot(url).to_png())


@app.agent(monitoring_topic)
async def monitor_url(urls):
    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        async for url in urls:
            executor.submit(Screenshot(url['url']).to_png())


@app.timer(interval=10, on_leader=True)
async def get_enabled():
    enabled_urls = Matches.objects(enabled=True)
    for match in enabled_urls:
        await monitoring_topic.send(value={'url': match['url']})

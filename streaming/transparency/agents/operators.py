from streaming.app import app
from streaming.config import config
from streaming.transparency.api.request import async_request
from streaming.transparency.topics import operators_topic
import faust

blacklist = config['transparency']['blacklist']
@app.timer(interval=10, on_leader=True)
async def get_operators():
    get_operators = await async_request(config['transparency']['base_url'])
    print('Syncing CT')
    if get_operators:
        for operator in get_operators['operators']:
            [await operators_topic.send(value={'log': log['url']}) for log in operator['logs'] \
                if log['url'] not in blacklist]

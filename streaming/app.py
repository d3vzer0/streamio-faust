from streaming.config import config
import logging
import faust

logging.config.fileConfig("streaming/logging.conf")
logger = logging.getLogger("streamio")

app = faust.App(config['stream']['name'], 
    broker=config['stream']['host'],
    autodiscover=[config['stream']['app']],
    stream_wait_empty=False,
    store=config['stream']['store'],
    partitions=config['stream']['partitions'])

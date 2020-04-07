from streaming.config import config
import faust

app = faust.App(config['stream']['name'], 
    broker=config['stream']['host'],
    autodiscover=[config['stream']['app']],
    partitions=8)

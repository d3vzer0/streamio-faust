from streaming.app import app

matched_topic = app.topic('wordmatching-hits')
monitoring_topic = app.topic('monitoring-urls')
screenshot_topic = app.topic('screenshot-results')

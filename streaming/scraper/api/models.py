from streaming.config import config
import mongoengine as db
import datetime

db.connect(
    db=config['mongo']['db'],
    host=config['mongo']['host'],
    port=config['mongo']['port'],
    username=config['mongo']['username'],
    password=config['mongo']['password'],
    authSource=config['mongo']['authsource']
)

source_options = ('transparency', 'phishtank')
matching_types = ('regex', 'fuzzy')


class Responses(db.EmbeddedDocument):
    response_code = db.IntField(required=False)
    response_data = db.StringField(required=False)

class Snapshots(db.Document):
    url = db.StringField(max_length=1000, required=True)
    timestamp = db.DateTimeField(required=False, default=datetime.datetime.now)
    response = db.EmbeddedDocumentField(Responses)
    sha256 = db.StringField(max_length=256, required=True)
    dhash = db.StringField(max_length=16)
    screenshot = db.FileField()

    meta = {
        'ordering': ['-timestamp'],
    }

class Matching(db.EmbeddedDocument):
    name = db.StringField(required=True, choices=matching_types)
    value = db.StringField(required=True, max_length=500)
    data = db.DictField(unique=True)

class Matches(db.Document):
    timestamp = db.DateTimeField(required=False, default=datetime.datetime.now)
    datasource = db.StringField(max_length=50, required=True, choices=source_options)
    matching = db.EmbeddedDocumentField(Matching)
    tags = db.ListField(db.StringField(max_length=50), default=list)

    url = db.StringField(max_length=1000, required=True)
    frequency = db.IntField(required=False, default=900)
    confirmed = db.BooleanField(required=False, default=False)
    enabled = db.BooleanField(required=False, default=False)


    meta = {
        'ordering': ['-timestamp'],
    }

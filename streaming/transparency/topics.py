
from streaming.app import app
from typing import Dict, List
import faust


class Tree(faust.Record):
    log: str
    tree_size: int
    timestamp: int
    sha256_root_hash: str
    tree_head_signature: str

class Operators(faust.Record):
    log: str

class States(faust.Record):
    tree_size: int
    old_size: int
    diff: int
    log: str

class EncodedCert(faust.Record):
    cert: Dict
    log: str





# State table containing last known record size
states_table = app.Table('ct-operators-state', default=int)

# Topic streaming latest transaprency sources/operators
operators_topic = app.topic('ct-operators', value_type=Operators)

tree_topic = app.topic('ct-tree-size', value_type=Tree)

# Topic streaming operators with changed records
states_topic = app.topic('ct-operators-changed', value_type=States)

# Topic streaming operators with changed records
states_topic = app.topic('ct-operators-changed', value_type=States)

# Topic with encoded certificates
cert_encoded_topic = app.topic('ct-certs-encoded', value_type=EncodedCert)

# Topic streaming recently issued certificates (decoded)
cert_decoded_topic = app.topic('ct-certs-decoded')


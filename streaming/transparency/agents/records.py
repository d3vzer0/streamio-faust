from streaming.app import app
from streaming.transparency.api import  MerkleTree
from streaming.transparency.topics import (
    EncodedCert, States, states_table,
    states_topic, cert_decoded_topic,
    cert_encoded_topic
)
import aiohttp
import faust
import httpx

async def async_records(log, range_start, range_end):
    try:
        range_start = range_start
        range_end = range_end
        async with httpx.AsyncClient() as client:
            while (range_end - range_start) >= 0:
                url = f'{log}ct/v1/get-entries?start={range_start}&end={range_end}'
                get_req = await client.get(url)
                all_entries = get_req.json()
                range_start += len(all_entries['entries'])
                for entry in all_entries['entries']:
                    yield entry
    except Exception as err:
        pass


# Get records for each operator
@app.agent(states_topic, concurrency=30) 
async def get_records(states: faust.Stream[States]):
    # Stream list of  operator whom assigned new certiifcates
    async for state in states:
        print(state)
        async for entry in async_records(state.log, state.old_size, state.tree_size):
            await cert_encoded_topic.send(value={'cert': entry, 'log': state.log})

# Decode each certificate to readable format
@app.agent(cert_encoded_topic)
async def decode_certs(certificates: faust.Stream[EncodedCert]):
    async for certificate in certificates.group_by(EncodedCert.log):
        try:
            states_table[certificate.log] += 1
            parsed_cert = MerkleTree(certificate.cert).parse()
            await cert_decoded_topic.send(value=parsed_cert)
        except Exception as err:
            print(err)
            pass

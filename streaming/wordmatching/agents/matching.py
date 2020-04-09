from streaming.wordmatching.api.match import Match
from streaming.wordmatching.api.models import Fuzzy, Regex, Whitelist
from streaming.wordmatching.api import Compare
from streaming.wordmatching.topics import cert_topic, matched_topic
from streaming.app import app
from faust import web
import re

filters = { 'regex': [], 'regex_raw':[], 'fuzzy': [], 'whitelist': [] }

@app.task
async def load_regex():
    try:
        filters['fuzzy'] = [{'value':entry['value'], 'likelihood':entry['likelihood']} for entry in Fuzzy.objects()]
        filters['whitelist'] = [entry['domain'] for entry in Whitelist.objects()]
        for entry in Regex.objects():
            filters['regex_raw'].append(entry['value'])
            filters['regex'].append(re.compile(entry['value']))
    except Exception as err:
        print('Invalid regex: {0}'.format(entry['value']))
        pass


@app.agent(cert_topic, concurrency=5)
async def regex_match_ct(certificates):
    async for certificate in certificates:
        if 'CN' in certificate['entry']['subject']:
            domain = certificate['entry']['subject']['CN']
            match_domain = Compare(domain, filters['whitelist']).regex(filters['regex'])
            if match_domain: await matched_topic.send(value={**match_domain, **{'proto':'https', 'data':certificate['entry'] } })

@app.agent(cert_topic, concurrency=5)
async def fuzzy_match_ct(certificates):
    async for certificate in certificates:
        if 'CN' in certificate['entry']['subject']:
            domain = certificate['entry']['subject']['CN']
            match_domain = Compare(domain, filters['whitelist']).fuzzy(filters['fuzzy'])
            if match_domain: await matched_topic.send(value={**match_domain, **{'proto':'https', 'data':certificate['entry'] } })


# Debug filters view
api_filters = web.Blueprint('api_filters')

@api_filters.route('/state', name='api_filters')
class APIFilters(web.View):
    async def get(self, request: web.Request) -> web.Response:
        result = {'fuzzy':filters['fuzzy'], 'regex':filters['regex_raw'],
            'whitelist':filters['whitelist']}
        return self.json(result)

@api_filters.route('/fuzzy', name='api_filters')
class APIFuzzy(web.View):
    async def get(self, request: web.Request) -> web.Response:
        filters['fuzzy'] = [{'value':entry['value'], 'likelihood':entry['likelihood']} for entry in Fuzzy.objects()]
        return self.json({'result': 'success', 'message':'Refreshed fuzzy'})

@api_filters.route('/regex', name='api_filters')
class APIRegex(web.View):
    async def get(self, request: web.Request) -> web.Response:
        try:
            filters['regex'] = []
            filters['regex_raw'] = []
            for entry in Regex.objects():
                filters['regex_raw'].append(entry['value'])
                filters['regex'].append(re.compile(entry['value']))
        except Exception as err:
            print('Invalid regex: {0}'.format(entry['value']))
            pass
        return self.json({'result': 'success', 'message':'Refreshed regex'})


@api_filters.route('/whitelist', name='api_filters')
class APIWhitelist(web.View):
    async def get(self, request: web.Request) -> web.Response:
        filters['whitelist'] = [entry['domain'] for entry in Whitelist.objects()]
        return self.json({'result': 'success', 'message':'Refreshed whitelist'})

app.web.blueprints.add('/filters/', api_filters)


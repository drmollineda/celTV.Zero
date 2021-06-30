from urllib2 import urlopen
import json


class ApiEndpoint(object):
    def __init__(self, target='%s'):
        self.target = target
        self.query_string = ''

    @staticmethod
    def __load_request(url):
        req = urlopen(url)
        res = json.loads(req.read())
        req.close()

        return res

    @staticmethod
    def encode(value):
        _ = json.dumps(value)
        return (_ if not _.startswith('"') else _[1:-1]).replace(' ', '')

    def query(self, action='', **kwargs):
        if kwargs is not None:
            if 'klass' in kwargs:
                kwargs['class'] = kwargs['klass']
                del kwargs['klass']
        else:
            kwargs = {}

        params = '&'.join('%s=%s' % (k, self.encode(v)) for k, v in kwargs.items())
        params = ('?%s' % params) if params else ''

        self.query_string = '%s%s' % (action, params)
        return self

    def __call__(self):
        return self.__load_request(self.target % self.query_string)


class Api(object):
    def __init__(self, address='127.0.0.1', port='9981'):
        self.api_base = 'http://%s:%s/api/' % (address, port)

        self.hardware = ApiEndpoint(self.api_base + 'hardware/%s')
        self.networks = ApiEndpoint(self.api_base + 'mpegts/network/%s')
        self.database = ApiEndpoint(self.api_base + 'idnode/%s')
        self.channels = ApiEndpoint(self.api_base + 'channel/%s')
        self.muxes = ApiEndpoint(self.api_base + 'mpegts/mux/%s')
        self.services = ApiEndpoint(self.api_base + 'mpegts/service/%s')
        self.channel_tags = ApiEndpoint(self.api_base + 'channeltag/%s')
        self.service_mapper = ApiEndpoint(self.api_base + 'service/mapper/%s')
        self.connections = ApiEndpoint(self.api_base + 'connections/%s')
        self.status = ApiEndpoint(self.api_base + 'status/%s')

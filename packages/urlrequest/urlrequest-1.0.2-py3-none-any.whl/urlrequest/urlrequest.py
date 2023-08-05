"""
    wrapper for urllib.request.urlopen
    very limited drop-in replacement for requests when you cant import requests
    and need to use the built in urllib.request library
"""

import urllib.request
import urllib.error
import json as jsonclass

class UrlRequest:
    """
        urllib.request in a class to make it easier to use
    """
    def __init__(self,
                url:str,
                data:str = None,
                json = None,
                method:str = 'GET',
                headers:dict = None,
                timeout:float = 10,
                auth:tuple = None):

        if headers is None: # python quirk with default mutables
            headers = {}

        # writes in a user agent if not there
        # default Python-urllib/X.X seems to be blocked by some
        if not headers.get('User-Agent'):
            headers['User-Agent'] = 'UrlRequest v1.0.2'

        if auth: # Basic Auth
            authhandle = urllib.request.HTTPPasswordMgrWithPriorAuth()
            authhandle.add_password(None, url, auth[0], auth[1],is_authenticated=True)
            opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(authhandle))
            urllib.request.install_opener(opener)

        if json: # json formatting and adding header
            headers['Content-Type'] = 'application/json'
            data = jsonclass.dumps(json)

        if isinstance(data,dict): # formatting dicts to urlencoded
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            output = ''
            for key,value in data.items():
                output = output + key + '=' + value + '&'
            data = output

        if data: # data formatting
            data = data.encode('utf-8',errors='ignore')

        req = urllib.request.Request(url,data=data,method=method,headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=timeout) as request:
                self._parseresponse(request)

        except urllib.error.HTTPError as exception:
            self._parseresponse(exception)

        # catches connection errors
        except urllib.error.URLError as exception:
            self.text = exception.reason
            self.status_code = None
            self.headers = {}
            self.json = {"Error": exception.reason}

    def _parseresponse(self,data):
        self.raw = data.read()
        self.text = self.raw.decode('utf-8',errors='backslashreplace')
        self.status_code = data.status
        self.headers = dict(data.headers)
        self.json = self._ifjson()

    def _ifjson(self):
        try:
            return jsonclass.loads(self.text)
        except jsonclass.JSONDecodeError:
            return None

    def __str__(self):
        return str(self.status_code)

    # next part is for drop-in replacement for requests
    # doesnt really do anything else
    # pylint: disable=no-self-argument,no-method-argument,missing-function-docstring
    def get(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='GET')
    def post(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='POST')
    def put(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='PUT')
    def delete(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='DELETE')
    def head(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='HEAD')
    def patch(*args,**kwargs):
        return UrlRequest(*args,**kwargs,method='PATCH')

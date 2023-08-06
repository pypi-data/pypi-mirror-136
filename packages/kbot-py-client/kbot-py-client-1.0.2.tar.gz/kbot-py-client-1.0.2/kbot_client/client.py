"""Dialog tester"""
import json
import requests

class Client:
    """Base representation of Kbot instance"""

    def __init__(self, server, port=443, proto='http'):

        self.host = server

        if str(port).endswith('443'):
            proto = 'https'
        else:
            proto = 'http'

        self.url = "%s://%s:%s"%(proto, server, port)

        self._login = False
        self._headers = {}

        # Variable populated by the login:
        self._user_id = None

        # Variable populated by the conversation
        self._cid = None

    @property
    def admin_url(self):
        """Returns the URL of the Kbot Administration view"""
        return "%s/admin" % self.url

    @property
    def chat_url(self):
        """Returns the default URL of the Kbot chat view"""
        return "%s" % self.url

    @property
    def avatar_url(self):
        return "%s/images/kbot_avatar.png" % self.url

    def login(self, username, password=None, slug='api-access'):
        """Login to local channel"""
        data = {}
        data['username'] = username
        data['usertype'] = 'local'
        if password is not None:
            data['password'] = password
        else:
            print("WARNING!!! Password is not set!!! Trying to use username...")
            data['password'] = username

        # First need to get the default application
        application = self._get_application(slug=slug)

        headers = {}
        headers['Content-Type'] = 'application/json'
        headers['Kbot-application-id'] = application["uuid"]

        url = self.url + '/api/login'
        r = requests.post(url, headers=headers, data=json.dumps(data), verify=False)

        if r.status_code != 200:
            print("ERROR. Failed to login! %s"%(r.text))
            raise RuntimeError("ERROR. Failed to login. Error: %s" % r.text)

        self._headers = {}
        self._headers['Authorization'] = r.json()['access_token']
        self._headers['Content-Type'] = 'application/json; charset=utf-8'
        self._login = True
        self._user_id = r.json()['user_id']

        self.schema()

    def schema(self):
        r = self._get('schema')
        if r.status_code != 200:
            print("ERROR. Failed to get login schema: %s"%(r.text))
            raise RuntimeError("ERROR. Failed to get schema. Error: %s" % r.text)

        j = r.json()
        #print(json.dumps(j, sort_keys=True, indent=4))
        for epoint in j.get('endpoints', []):
            if epoint['name'] != 'schema':
                self.__add_method(epoint['method'], epoint['name'], epoint['path'], epoint['params'], epoint['data'], epoint.get('description', ''))

    def __add_method(self, method: str, name: str, path: str, params: list, data: list, description: str):
        def endpoint(*args, **kwargs):
            """Invoke request to endpoint"""
            rargs = {}
            for aname, values in (('params', params), ('data', data)):
                rargs[aname] = {}
                for value in values:
                    if value['mandatory'] and value['name'] not in kwargs:
                        raise RuntimeError("Missed attribute '%s' in '%s'"%(value['name'], aname))
                    # pylint: disable=eval-used
                    if value['name'] in kwargs:
                        if not isinstance(kwargs[value['name']], eval(value['type'])):
                            raise RuntimeError("Invalid type of attribute '%s'"%(value['name']))
                        v = kwargs[value['name']]
                    elif value['name'] not in kwargs and value['default'] is not None:
                        v = value['default']
                    else:
                        continue
                    rargs[aname][value['name']] = v
            return self.__request(method, path % args, **rargs)
        endpoint.__doc__ = description
        endpoint.__name__ = name
        setattr(self, name, endpoint)

    def __request(self, method: str, unit: str, data: dict = None, params: dict = None):
        dump_data = json.dumps(data or {})
        r = requests.request(method.upper(), self.url + '/api/%s/'%(unit), params=params, data=dump_data, headers=self._headers)
        return r

    def _get_application(self, slug='api-access'):
        #
        headers = {}
        headers['Content-Type'] = 'application/json'

        # We can put the slug of the Application.
        # We use api-access as it is garanteed to have 'local' access
        headers['Referer'] = self.url + '/' + slug

        r = requests.get(self.url + '/api/application/current', headers=headers)

        if r.status_code != 200:
            print("ERROR. Failed to get application: %s" % (r.text))
            raise RuntimeError("ERROR. Failed to get application!")
        return r.json()

    def logout(self):
        """Logout from local channel"""
        if self._login:

            # If we have an open conversation, close it.
            #if self._cid:
                # What for?
                # self._process('logout', 1)

            # Logout from the APIs
            requests.post(self.url + '/api/logout', headers=self._headers)

    def _get(self, unit, params=None):
        r = requests.get(self.url + '/api/%s/'%(unit), params=params, headers=self._headers)

        if r.status_code in (200, 206):
            return r

        return None

    def _put(self, unit, data, params=None):
        return requests.put(self.url + '/api/%s/'%(unit), params=params, data=json.dumps(data), headers=self._headers)

    def _post(self, unit, data, params=None):
        return requests.post(self.url + '/api/%s/'%(unit), params=params, data=json.dumps(data), headers=self._headers)

    def _delete(self, unit, params=None):
        return requests.delete(self.url + '/api/%s/'%(unit), params=params, headers=self._headers)


class UpKbotClient(Client):
    """Represents a currently reachable Kbot instance"""

class DownKbotClient(Client):
    """Represents a currently not reachable Kbot instance"""

    def __init__(self, server, port=443, proto='http', error=''):
        super().__init__(server, port=port, proto=proto)
        self.error = error

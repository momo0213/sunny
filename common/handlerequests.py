
import requests
class HandleRequests(object):
    '''cookie+session鉴权'''

    def __init__(self):
        self.seesion = requests.session()

    def send_requests(self, method, url, headers=None, params=None, json=None, data=None, files=None):
        method = method.lower()
        if method == "post":
            response = self.seesion.post(url=url, headers=headers, json=json, data=data, files=files)
        if method == "get":
            response = self.seesion.get(url=url, headers=headers, params=params)
        if method == "patch":
            response = self.seesion.patch(url=url, headers=headers, json=json, data=data, files=files)
        return response
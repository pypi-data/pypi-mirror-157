# Module file: decoderpy.py

from queue import Empty
import requests

__name__="sender"

def send(data={}, config={ "token": Empty, "account": Empty, "endpoint": Empty}, callback = lambda resp : print(resp)):
    response = requests.post('https://httpbin.org/post', data = {'key':'value'})

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(config['token'])
    }

    url = "https://{0}.api.decodable.co{1}".format(config["account"], config["endpoint"])

    response = requests.post(url, headers=headers, data=data)
    callback(response)

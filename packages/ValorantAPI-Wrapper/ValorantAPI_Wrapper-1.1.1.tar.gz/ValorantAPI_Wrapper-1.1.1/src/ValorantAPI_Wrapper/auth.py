import urllib3
import requests
import re
from  requests.adapters import HTTPAdapter
from typing import Any
import ssl
from collections import OrderedDict

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

username = ""
password = ""
region = "" 

FORCED_CIPHERS = [
    'ECDHE-ECDSA-AES128-GCM-SHA256',
    'ECDHE-ECDSA-CHACHA20-POLY1305',
    'ECDHE-RSA-AES128-GCM-SHA256',
    'ECDHE-RSA-CHACHA20-POLY1305',
    'ECDHE+AES128',
    'RSA+AES128',
    'ECDHE+AES256',
    'RSA+AES256',
    'ECDHE+3DES',
    'RSA+3DES'
]

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args: Any, **kwargs: Any) -> None:
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        #ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        ctx.set_ciphers(':'.join(FORCED_CIPHERS))
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

class Auth:

    def __init__(self, auth):
        self.username = auth['username']
        self.password = auth['password']

    def authenticate(self):

        headers = OrderedDict({
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "application/json, text/plain, */*"
        })

        session = requests.session()
        session.headers = headers
        session.mount('https://', TLSAdapter())

        data = {
            'client_id': 'play-valorant-web-prod',
            'nonce': '1',
            'redirect_uri': 'https://playvalorant.com/opt_in',
            'response_type': 'token id_token',
            'scope': 'account openid',
        }

        headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'RiotClient/51.0.0.4429735.4381201 rso-auth (Windows;10;;Professional, x64)',
        }   
        r = session.post(f'https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)
        #print(r.text)
        
        data = {
            'type': 'auth',
            'username': self.username,
            'password': self.password
        }
        r = session.put(f'https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)
        data = r.json()
        if data["type"] == "auth" or data["type"] == "error":
            session.close()
            return 0
        pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
        data = pattern.findall(r.json()['response']['parameters']['uri'])[0]
        access_token = data[0]
        # print('Access Token: ' + access_token)

        headers = {
            'User-Agent': 'RiotClient/51.0.0.4429735.4381201 rso-auth (Windows;10;;Professional, x64)',
            'Authorization': f'Bearer {access_token}',
        }
        r = session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={})
        entitlements_token = r.json()['entitlements_token']
        # print('Entitlements Token: ' + entitlements_token)

        headers = {
            'User-Agent': 'RiotClient/51.0.0.4429735.4381201 rso-auth (Windows;10;;Professional, x64)',
            'Authorization': f'Bearer {access_token}',
        }

        r = session.post('https://auth.riotgames.com/userinfo', headers=headers, json={})
        user_id = r.json()['sub']
        # print('User ID: ' + user_id)
        headers['X-Riot-Entitlements-JWT'] = entitlements_token
        session.close()
        Authorization= headers["Authorization"]
        en_token = headers['X-Riot-Entitlements-JWT']
        return user_id, Authorization, en_token, headers
import requests
import hashlib
import hmac

requests.packages.urllib3.disable_warnings()


def param2string(param):
    s = ''
    for k in param.keys():
        s += k
        s += '='
        s += str(param[k])
        s += '&'
    return s[:-1]


class BinanceAPI:
    def __init__(self, base_url, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url

    def api(self, method, request_path, body):
        header = {
            'Connection': 'close',
            'X-MBX-APIKEY': self.api_key,
        }
        if request_path != '/dapi/v1/depth' and request_path != '/api/v3/depth':
            body['signature'] = hmac.new(self.secret_key.encode('utf-8'), param2string(body).encode('utf-8'),
                                         hashlib.sha256).hexdigest()
        if method == 'GET':
            body = param2string(body)
            response = requests.get(url=f'{self.base_url}{str(request_path)}', headers=header, params=body,
                                    verify=False)
            try:
                result = response.json()  # GET方法
                response.close()
                return result
            except Exception as e:
                print(f'respond = {response}')
                raise ValueError(e)
        elif method == 'POST':
            response = requests.post(url=f'{self.base_url}{str(request_path)}', headers=header, data=body, verify=False)
            try:
                result = response.json()  # POST方法
                response.close()
                return result
            except Exception as e:
                print(e)
                print(f'respond = {response}')
                print(f'respond = {response.text}')
        elif method == 'DELETE':
            response = requests.delete(url=f'{self.base_url}{str(request_path)}', headers=header, params=body,
                                       verify=False)
            try:
                result = response.json()  # DELETE方法
                response.close()
                return result
            except Exception as e:
                print(e)
                print(f'respond = {response}')
                print(f'respond = {response.text}')

import requests

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 SLBrowser/9.0.0.10191 SLBChan/25',
}

json_data = {
    'pageNumber': 200,
    'pageSize': 50,
    'timeRange': '7D',
    'dataType': 'SHARP_RATIO',
    'favoriteOnly': False,
    'hideFull': True,
    'nickname': '',
    'order': 'DESC',
    'userAsset': 0.25143313,
    'portfolioType': 'PUBLIC',
}

response = requests.post(
    'https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/home-page/query-list',
    headers=headers,
    json=json_data,
)
print(response.json())
print(len(response.json()['data']['list']))
import random
l = [1,2,3,4,5,6,7,8,9,10]
print(random.choice(l))

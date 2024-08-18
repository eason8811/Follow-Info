import json
import time
import matplotlib.pyplot as plt
import numpy as np
import requests
import random
from tqdm import tqdm
from BinanceAPI import BinanceAPI


def normalize(lst):
    lst = np.array(lst)
    result = (lst - lst.min()) / (lst.max() - lst.min())
    return result


base_url = 'https://fapi.binance.com'
api_key = 'i7F6rx3Tcz6eJlSVzBc4dpV6qyszCiCOIpSz7gv9mdyq9UjVizrlu2kkmlvUIJSw'
secret_key = 'mwU7KCworFZ17WIOqRuGaRmtwT3nnUDBhtg8HQf9CHFB7KVSxev0Rwym5mgfWjDx'

u_api = BinanceAPI(base_url, api_key, secret_key)

# 爬取参数
kline_amount = 2880
period = 15  # 分钟

top_position_ratio = []
top_account_ratio = []
amount = kline_amount
while amount > 0:
    body = {
        'symbol': 'BTCUSDT',
        'period	': '15m',
        'limit': min(500, amount)
    }
    respond = u_api.api('GET', '/futures/data/topLongShortPositionRatio', body)
    top_position_ratio.extend(respond)
    respond = u_api.api('GET', '/futures/data/topLongShortAccountRatio', body)
    top_account_ratio.extend(respond)
    print(f'\r{round((2880 - amount) / 2880, 5) * 100}%', end='')
    amount -= 500

klines = []
amount = kline_amount
end_time = int(time.time()) * 1000
while amount > 0:
    body = {
        'symbol': 'BTCUSDT',
        'interval': '15m',
        'endTime': end_time,
        'limit': min(1500, amount)
    }
    respond = u_api.api('GET', '/fapi/v1/klines', body)
    for item in respond:
        kline = {
            'time': item[0],
            'open': float(item[1]),
            'high': float(item[2]),
            'low': float(item[3]),
            'close': float(item[4]),
        }
        klines.append(kline)
    amount -= 1500
    end_time -= period * 60 * 1000

close_data = normalize(list(map(lambda x: x['close'], klines)))  # 收盘价
long_short_position_ratio = normalize(list(map(lambda x: x['longShortRatio'], top_position_ratio)))  # 大户多空持仓量比值
long_position = normalize(list(map(lambda x: x['longAccount'], top_position_ratio)))  # 大户持的多仓量占全市场比值
short_position = normalize(list(map(lambda x: x['shortAccount'], top_position_ratio)))  # 大户持的空仓量占全市场比值
long_short_account_ratio = normalize(list(map(lambda x: x['longShortRatio'], top_position_ratio)))  # 大户多空持仓账户比值
long_account = normalize(list(map(lambda x: x['longAccount'], top_position_ratio)))  # 大户持的多仓账户数占全市场的比值
short_account = normalize(list(map(lambda x: x['shortAccount'], top_position_ratio)))  # 大户持的空仓账户数占全市场的比值

plt.plot(list(map(lambda x: x['time'], close_data)), close_data, label='close')
plt.plot(list(map(lambda x: x['time'], close_data)), long_short_position_ratio, label='long_short_position_ratio')
# plt.plot(list(map(lambda x: x['time'], close_data)), long_position, label='long_position')
# plt.plot(list(map(lambda x: x['time'], close_data)), short_position, label='short_position')
# plt.plot(list(map(lambda x: x['time'], close_data)), long_short_account_ratio, label='long_short_account_ratio')
# plt.plot(list(map(lambda x: x['time'], close_data)), long_account, label='long_account')
# plt.plot(list(map(lambda x: x['time'], close_data)), short_account, label='short_account')

plt.legend()
plt.ticklabel_format(useOffset=False, style='plain')
plt.grid(axis='both')
plt.show()

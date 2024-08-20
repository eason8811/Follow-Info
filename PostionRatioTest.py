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
kline_amount = 2800
period = 15  # 分钟

top_position_ratio = []
top_account_ratio = []
amount = kline_amount
end_time = int(time.time()) * 1000
while amount > 0:
    body = {
        'symbol': 'BTCUSDT',  # 0                       -1                  0                     -1
        'period': '15m',  # 2024-08-14 06:15:00  2024-08-19 11:00:00  2024-08-09 00:30:00  2024-08-14 06:00:00
        'endTime': end_time,
        # 1723587300000        1724036400000        1723134600000        1723586400000  1722687300000  1723136400000
        'limit': min(500, amount)
    }
    respond = u_api.api('GET', '/futures/data/topLongShortPositionRatio', body)
    respond.reverse()
    for i in range(len(respond)):
        respond[i]['longShortRatio'] = float(respond[i]['longShortRatio'])
        respond[i]['longAccount'] = float(respond[i]['longAccount'])
        respond[i]['shortAccount'] = float(respond[i]['shortAccount'])
    top_position_ratio.extend(respond)
    respond = u_api.api('GET', '/futures/data/topLongShortAccountRatio', body)
    respond.reverse()
    for i in range(len(respond)):
        respond[i]['longShortRatio'] = float(respond[i]['longShortRatio'])
        respond[i]['longAccount'] = float(respond[i]['longAccount'])
        respond[i]['shortAccount'] = float(respond[i]['shortAccount'])
    top_account_ratio.extend(respond)
    print(f'\r{round((2880 - amount) / 2880 * 100, 3)}%', end='')
    amount -= 500
    end_time -= period * 60 * 1000 * 500
print('\r大数据获取完成')
top_position_ratio.reverse()
top_account_ratio.reverse()

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
    respond.reverse()
    for item in respond:
        kline = {
            'time': item[0],
            'open': float(item[1]),
            'high': float(item[2]),
            'low': float(item[3]),
            'close': float(item[4]),
        }
        klines.append(kline)
    print(f'\r{round((2880 - amount) / 2880 * 100, 3)}%', end='')
    amount -= 1500
    end_time -= period * 60 * 1000 * 1500
print('\rK线数据获取完成')
klines.reverse()

with open('data.json', 'w') as f:
    data = {
        'close': list(map(lambda x: x['close'], klines)),
        'short_position':list(map(lambda x: x['shortAccount'], top_position_ratio)),
    }
    f.write(json.dumps(data))

close_data = normalize(list(map(lambda x: x['close'], klines)))  # 收盘价
long_short_position_ratio = normalize(list(map(lambda x: x['longShortRatio'], top_position_ratio)))  # 大户多空持仓量比值
long_position = normalize(list(map(lambda x: x['longAccount'], top_position_ratio)))  # 大户持的多仓量占全市场比值
short_position = normalize(list(map(lambda x: x['shortAccount'], top_position_ratio)))  # 大户持的空仓量占全市场比值
long_short_account_ratio = normalize(list(map(lambda x: x['longShortRatio'], top_account_ratio)))  # 大户多空持仓账户比值
long_account = normalize(list(map(lambda x: x['longAccount'], top_account_ratio)))  # 大户持的多仓账户数占全市场的比值
short_account = normalize(list(map(lambda x: x['shortAccount'], top_account_ratio)))  # 大户持的空仓账户数占全市场的比值

# plt.plot(list(map(lambda x: x['time'] / 1000, klines)), close_data, label='close')
# plt.plot(list(map(lambda x: x['time'] / 1000, klines)), list(long_short_position_ratio),
#          label='long_short_position_ratio')
# plt.plot(list(map(lambda x: x['time']/1000, klines)), long_position, label='long_position')
# plt.plot(list(map(lambda x: x['time']/1000, klines)), short_position, label='short_position')
# plt.plot(list(map(lambda x: x['time']/1000, klines)), long_short_account_ratio, label='long_short_account_ratio')
# plt.plot(list(map(lambda x: x['time']/1000, klines)), long_account, label='long_account')
# plt.plot(list(map(lambda x: x['time']/1000, klines)), short_account, label='short_account')

lst = [long_short_position_ratio, long_position, short_position, long_short_account_ratio, long_account, short_account]
label_lst = ['long_short_position_ratio', 'long_position', 'short_position', 'long_short_account_ratio', 'long_account',
             'short_account']
for i in range(len(lst)):
    plt.clf()
    plt.plot(list(map(lambda x: x['time'] / 1000, klines)), close_data, label='close')
    plt.plot(list(map(lambda x: x['time'] / 1000, klines)), lst[i], label=label_lst[i])
    plt.ticklabel_format(useOffset=False, style='plain')
    plt.grid(axis='both')
    plt.legend()
    plt.savefig(f'pic/{label_lst[i]}.png')
    # plt.show()

plt.clf()
plt.plot(list(map(lambda x: x['time'] / 1000, klines)), close_data, label='close')
# plt.plot(list(map(lambda x: x['time']/1000, klines)), long_position, label='long_position')
plt.plot(list(map(lambda x: x['time'] / 1000, klines)), short_position, label='short_position')
# plt.plot(list(map(lambda x: x['time']/1000, klines)), np.array(long_position) + np.array(short_position), label='short_position')
plt.legend()
plt.ticklabel_format(useOffset=False, style='plain')
plt.grid(axis='both')
plt.show()

plt.clf()
offset = 50
# for i in range(offset):
#     plt.clf()
#     # plt.plot(list(map(lambda x: x['time'] / 1000, klines))[i:], close_data[i:], label='close')
#     # plt.plot(list(map(lambda x: x['time'] / 1000, klines))[i:], short_position[:len(short_position) - i],
#     #          label='short_position')
#     plt.plot(list(map(lambda x: x['time'] / 1000, klines))[i:],
#              close_data[i:] - short_position[:len(short_position) - i],
#              label='short_position')
#     plt.ticklabel_format(useOffset=False, style='plain')
#     plt.grid(axis='both')
#     plt.legend()
#     plt.savefig(f'offsetPic/{i}.png')
print('已完成绘图')

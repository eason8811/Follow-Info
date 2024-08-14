import json
import time
import matplotlib.pyplot as plt
import numpy as np
import requests
import random
from tqdm import tqdm
from BinanceFollowAPI import Binance

binance = Binance()

# leader_list = binance.get_leader_list()
# # print(leader_list)
#
# position_list = binance.get_all_position_symbol(leader_list, 'BTCUSDT')
# # print(position_list)
# with open('position_list.json', 'w') as f:
#     f.write(json.dumps(position_list))

with open('position_list.json', 'r') as f:
    position_list = json.loads(f.read())

print(len(position_list))
position_list_symbol = []
earliest_open_time = int(time.mktime(time.localtime()) * 1000)
for position in tqdm(position_list):
    if position['symbol'] == 'BTCUSDT':
        earliest_open_time = min(earliest_open_time, int(position['opened']))
        position_list_symbol.append(position)

position_amount = {}
position_count = {}
now_time = int(time.mktime(time.localtime()) * 1000)
# init
for i in tqdm(range(earliest_open_time // (15 * 60 * 1000) * (15 * 60 * 1000), now_time, 60 * 15 * 1000)):
    position_amount[i] = [0, 0]  # [long, short]
    position_count[i] = [0, 0]  # [long, short]

for position in tqdm(position_list_symbol):
    if position['side'] == 'Long':
        belong_open_time = int(position['opened']) // (15 * 60 * 1000) * (15 * 60 * 1000)
        belong_close_time = int(position['updateTime']) // (15 * 60 * 1000) * (15 * 60 * 1000)
        for i in range(belong_open_time, belong_close_time + (60 * 15 * 1000), 60 * 15 * 1000):
            position_amount[i][0] += float(position['maxOpenInterest']) * float(position['avgCost'])
            position_count[i][0] += 1
    elif position['side'] == 'Short':
        belong_open_time = int(position['opened']) // (15 * 60 * 1000) * (15 * 60 * 1000)
        belong_close_time = int(position['updateTime']) // (15 * 60 * 1000) * (15 * 60 * 1000)
        for i in range(belong_open_time, belong_close_time + (60 * 15 * 1000), 60 * 15 * 1000):
            position_amount[i][1] += float(position['maxOpenInterest']) * float(position['avgCost'])
            position_count[i][1] += 1

print(position_amount)
print(position_count)

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

klines_data = binance.get_kline_symbol('BTCUSDT', '15m', 2880, 1722996900000)
color_list = []
for kline in klines_data:
    color = 'green' if kline['close'] > kline['open'] else 'red'
    color_list.append(color)
    ax1.vlines(x=kline['time'], ymin=kline['low'], ymax=kline['high'], color=color)
ax1.bar(x=list(map(lambda x: x['time'], klines_data)),
        height=list(map(lambda x: abs(x['close']-x['open']), klines_data)),
        bottom=list(map(lambda x: min(x['open'], x['close']), klines_data)),
        color=color_list, width=15*60*1000)


ax2.plot(list(position_amount.keys())[-2880-672:-672], [position_amount[i][0] for i in position_amount.keys()][-2880-672:-672], label='long_amount')
ax2.plot(list(position_amount.keys())[-2880-672:-672], [position_amount[i][1] for i in position_amount.keys()][-2880-672:-672], label='short_amount')
ax2.plot(list(position_count.keys())[-2880-672:-672], [position_count[i][0]*30000 for i in position_count.keys()][-2880-672:-672], label='long_count')
ax2.plot(list(position_count.keys())[-2880-672:-672], [position_count[i][1]*30000 for i in position_count.keys()][-2880-672:-672], label='short_count')
plt.legend()
plt.ticklabel_format(useOffset=False, style='plain')
ax1.grid(axis='both')
plt.show()

fig.clear()
close_line = np.array(list(map(lambda x: x['close'], klines_data))[-2880-672:-672])
long_amount = np.array([position_amount[i][0] for i in position_amount.keys()][-2880-672:-672])
short_amount = np.array([position_amount[i][1] for i in position_amount.keys()][-2880-672:-672])
long_count = np.array([position_count[i][0]*30000 for i in position_count.keys()][-2880-672:-672])
short_count = np.array([position_count[i][1]*30000 for i in position_count.keys()][-2880-672:-672])
ax1.plot(list(position_amount.keys())[-2880-672:-672], close_line-long_amount, label='close-long_amount')
ax1.plot(list(position_amount.keys())[-2880-672:-672], close_line-short_amount, label='close-short_amount')
ax1.plot(list(position_count.keys())[-2880-672:-672], close_line-long_count, label='close-long_count')
ax1.plot(list(position_count.keys())[-2880-672:-672], close_line-short_count, label='close-short_count')
plt.legend()
plt.ticklabel_format(useOffset=False, style='plain')
ax1.grid(axis='both')
plt.show()


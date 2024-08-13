import json
import time

import requests
import random
from tqdm import tqdm
from Binance_API import Binance

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
for i in range(earliest_open_time, now_time, 60 * 15 * 1000):
    position_amount[i] = [0, 0]  # [long, short]
    position_count[i] = [0, 0]  # [long, short]

for position in position_list_symbol:
    if position['side'] == 'LONG':
        belong_open_time = int(position['opened']) // (15 * 60 * 1000) * (15 * 60 * 1000)
        belong_close_time = int(position['updateTime']) // (15 * 60 * 1000) * (15 * 60 * 1000)
        for i in range(belong_open_time, belong_close_time + (60 * 15 * 1000), 60 * 15 * 1000):
            position_amount[i][0] += float(position['positionAmt'])
            position_count[i][0] += 1
    elif position['side'] == 'SHORT':
        belong_open_time = int(position['opened']) // (15 * 60 * 1000) * (15 * 60 * 1000)
        belong_close_time = int(position['updateTime']) // (15 * 60 * 1000) * (15 * 60 * 1000)
        for i in range(belong_open_time, belong_close_time + (60 * 15 * 1000), 60 * 15 * 1000):
            position_amount[i][1] += float(position['positionAmt'])
            position_count[i][1] += 1

print(position_amount)
print(position_count)



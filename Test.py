import json
import requests
import random

from Binance_API import Binance

binance = Binance()

leader_list = binance.get_leader_list()
# print(leader_list)

position_list = binance.get_all_position_symbol(leader_list, 'BTCUSDT')
# print(position_list)
with open('position_list.json', 'w') as f:
    f.write(json.dumps(position_list))
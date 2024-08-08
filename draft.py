import requests
import random

from Binance_API import Binance

binance = Binance()

leader_list = binance.get_leader_list()
# print(leader_list)

print(binance.get_all_position_symbol(leader_list, 'BTCUSDT'))
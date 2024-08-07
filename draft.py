import requests
import random

from Binance_API import Binance

binance = Binance()

binance.get_leader_list()
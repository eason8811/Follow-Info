import requests
import asyncio
import aiohttp
import random
from GetProxies import get_proxies


class Leader:
    def __init__(self, aum, current_copy_count, leader_id, max_count, mdd, name, pnl, roi, sharp_ratio, win_rate):
        """
        :param aum: 当前项目保证金
        :param current_copy_count: 当前复制的人数
        :param leader_id: 带单员ID
        :param max_count: 项目最大跟单人数
        :param mdd: 回撤
        :param name: 项目名字
        :param pnl: 项目盈利额
        :param roi: 项目盈利率
        :param sharp_ratio: 夏普比率
        :param win_rate: 胜率
        """
        self.aum = aum
        self.current_copy_count = current_copy_count
        self.leader_id = leader_id
        self.max_count = max_count
        self.mdd = mdd
        self.name = name
        self.pnl = pnl
        self.roi = roi
        self.sharp_ratio = sharp_ratio
        self.win_rate = win_rate


class Binance(object):
    def __init__(self):
        # self.proxies = get_proxies(4, 4)
        pass

    async def leader_4_a_page(self, page_number):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 SLBrowser/9.0.0.10191 SLBChan/25',
        }

        json_data = {
            'pageNumber': page_number,
            'pageSize': 50,
            'timeRange': '7D',
            'dataType': 'PNL',
            'favoriteOnly': False,
            'hideFull': True,
            'nickname': '',
            'order': 'DESC',
            'userAsset': 0.25143313,
            'portfolioType': 'PUBLIC',
        }

        url = 'https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/home-page/query-list'

        async with aiohttp.ClientSession() as session:
            # async with session.post(url, json=json_data, headers=headers,
            #                         proxy=random.choice(self.proxies)['http']) as respond:
            async with session.post(url, json=json_data, headers=headers) as respond:
                if respond.status == 200:
                    leader_list = await respond.json()
                    return leader_list['data']['list']

        # if response.get('data') and response.get('data').get('list') and len(response.get('data').get('list')) > 0:
        #     for item in response.get('data').get('list'):
        #         leader = Leader(item['aum'], item['currentCopyCount'], item['leadPortfolioId'],
        #                         item['maxCopyCount'], item['mdd'], item['nickname'], item['pnl'], item['roi'],
        #                         item['sharpRatio'], item['winRate'])
        #         leader_list.append(leader)

    async def leader_4_all_page(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 SLBrowser/9.0.0.10191 SLBChan/25',
        }

        json_data = {
            'pageNumber': 1,
            'pageSize': 50,
            'timeRange': '7D',
            'dataType': 'PNL',
            'favoriteOnly': False,
            'hideFull': True,
            'nickname': '',
            'order': 'DESC',
            'userAsset': 0.25143313,
            'portfolioType': 'PUBLIC',
        }

        url = 'https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/home-page/query-list'
        response = requests.post(url, headers=headers, json=json_data).json()
        total_page = int(int(response['data']['total']) / 50) + 1

        tasks = []
        for page in range(1, total_page + 1):
            task = asyncio.create_task(self.leader_4_a_page(page))
            tasks.append(task)
        await asyncio.wait(tasks)
        result = []
        for task in tasks:
            result.extend(task.result())
        print(result)

    def get_leader_list(self):
        # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        # asyncio.run(self.leader_4_all_page())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.leader_4_all_page())


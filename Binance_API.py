import time

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
        # self.proxies = get_proxies(15, 4)
        # print(self.proxies)
        pass

    async def __leader_4_a_page(self, page_number):
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

    async def __leader_4_all_page(self):
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
            task = asyncio.create_task(self.__leader_4_a_page(page))
            tasks.append(task)
        await asyncio.wait(tasks)
        leader_list = []
        for task in tasks:
            leader_list.extend(task.result())

        result = []
        for item in leader_list:
            leader = Leader(item['aum'], item['currentCopyCount'], item['leadPortfolioId'],
                            item['maxCopyCount'], item['mdd'], item['nickname'], item['pnl'], item['roi'],
                            item['sharpRatio'], item['winRate'])
            result.append(leader)
        return result

    def get_leader_list(self):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.__leader_4_all_page())

    async def __position_4_a_page(self, page_number, symbol, leader_id):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 SLBrowser/9.0.0.10191 SLBChan/25',
        }

        json_data = {
            'pageNumber': page_number,
            'pageSize': 50,
            'portfolioId': leader_id,
            'sort': 'OPENING',
        }

        url = 'https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/lead-portfolio/position-history'

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_data, headers=headers) as respond:
                    if respond.status == 200:
                        result = []
                        position_list = await respond.json()
                        position_list = position_list['data']['list']
                        for position in position_list:
                            # if position['symbol'] == symbol:
                            #     result.append(position)
                            result.append(position)
                        return result
                    else:
                        # print(await respond.text())
                        print(json_data)
                        await asyncio.sleep(15)
                        task = asyncio.create_task(self.__position_4_a_page(page_number, symbol, leader_id))
                        await asyncio.wait([task,])
                        return task.result()
        except Exception as exc:
            print(exc)
            print(json_data)
            await asyncio.sleep(15)
            task = asyncio.create_task(self.__position_4_a_page(page_number, symbol, leader_id))
            await asyncio.wait([task, ])
            return task.result()

    async def __get_total_postion_page(self, leader):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 SLBrowser/9.0.0.10191 SLBChan/25',
        }
        url = 'https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/lead-portfolio/position-history'

        json_data = {
            'pageNumber': 1,
            'pageSize': 50,
            'portfolioId': leader.leader_id,
            'sort': 'OPENING',
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json_data, headers=headers) as respond:
                if respond.status == 200:
                    respond_json = await respond.json()
                    total_page = int(int(respond_json['data']['total']) / 50) + 1
                    return total_page

    async def __position_4_a_leader(self, symbol, i, leader_list, total_page_list):
        tasks = []
        total_page = total_page_list[i]
        leader = leader_list[i]
        for page in range(1, total_page + 1):
            # print(f'total {i + 1} page {page} 开始')
            task = asyncio.create_task(self.__position_4_a_page(page, symbol, leader.leader_id))
            tasks.append(task)
        await asyncio.wait(tasks)
        position_list = []
        for task in tasks:
            position_list.extend(task.result())
        return position_list

    async def __position_4_all_leader(self, leader_list, symbol):
        total_page_list = []
        for j in range(0, len(leader_list), int(len(leader_list) / 20)):
            if j + int(len(leader_list) / 20) < len(leader_list):
                leader_slice = leader_list[j:j + int(len(leader_list) / 20)]
            else:
                leader_slice = leader_list[j:]
            tasks = []
            for leader in leader_slice:
                print(f'total {leader_list.index(leader) + 1} 开始')
                task = asyncio.create_task(self.__get_total_postion_page(leader))
                tasks.append(task)
            await asyncio.wait(tasks)
            for task in tasks:
                total_page_list.append(task.result())

        print(total_page_list)

        result = []
        start = 0
        end = 0
        start_time = time.mktime(time.localtime())
        while end < len(leader_list):
            if end == 0:
                page_count = 0
                while page_count < 1000 and end < len(leader_list):
                    page_count += total_page_list[end]
                    end += 1
            else:
                start = end
                page_count = 0
                while page_count < 1000 and end < len(leader_list):
                    page_count += total_page_list[end]
                    end += 1
            tasks = []
            time.sleep(3)
            print(f'{end - start} 个 leader 共 {page_count} 页')
            for i in range(start, end):
                task = asyncio.create_task(self.__position_4_a_leader(symbol, i, leader_list, total_page_list))
                tasks.append(task)
            await asyncio.wait(tasks)
            print(f'{end} 个 leader 共 {sum(total_page_list[:end])} 页 已完成！')
            # time.sleep(15)
            try:
                for task in tasks:
                    result.extend(task.result())
            except:
                print(f'已进行: {sum(total_page_list[:end])}页  将重试!')  # 3921
        print(f'总使用时间为{time.mktime(time.localtime()) - start_time} s')
        return result

    def get_all_position_symbol(self, leader_list, symbol):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.__position_4_all_leader(leader_list, symbol))

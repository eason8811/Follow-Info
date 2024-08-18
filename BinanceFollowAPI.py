import time
import requests_async
import requests
import asyncio
import aiohttp
import random
from GetProxies import get_proxies
from BinanceAPI import BinanceAPI


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

    def __str__(self):
        str_result = {
            'aum': self.aum,
            'current_copy_count': self.current_copy_count,
            'leader_id': self.leader_id,
            'max_count': self.max_count,
            'mdd': self.mdd,
            'name': self.name,
            'pnl': self.pnl,
            'roi': self.roi,
            'sharp_ratio': self.sharp_ratio,
            'win_rate': self.win_rate
        }
        return f'{str_result}\n'


class Binance:
    def __init__(self):
        # self.proxies = get_proxies(15, 4)
        # print(self.proxies)
        pass

    async def __leader_4_a_page(self, page_number):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
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

        respond = requests_async.post(url, json=json_data, headers=headers)
        respond = await respond
        if respond.status_code == 200:
            leader_list = respond.json()
            return leader_list['data']['list']

    async def __leader_4_all_page(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
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

    async def __position_4_a_page(self, page_number, leader_id):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        }

        json_data = {
            'pageNumber': page_number,
            'pageSize': 50,
            'portfolioId': leader_id,
        }

        url = 'https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/lead-portfolio/trade-history'

        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=json_data, headers=headers) as respond:

                        if respond.status == 200:
                            result = []
                            position_list = await respond.json()
                            position_list = position_list['data']['list']
                            for position in position_list:
                                result.append(position)
                            return {leader_id: result}
                        else:
                            # print(respond.status)
                            # print(f"Retry-After={respond.headers}")
                            # print(await respond.text())
                            # print(json_data)
                            print(f'http  {page_number} 未完成')
                            await asyncio.sleep(5)
                            continue
            except Exception as exc:
                # print(exc)
                # print(respond.status)
                # print(await respond.text())
                # print(json_data)
                # print(f'error  {page_number} 未完成')
                print(f'{leader_id} 出错')
                await asyncio.sleep(5)
                continue

    async def __position_4_a_leader(self, symbol, i, leader_list, total_page_list):
        tasks = []
        total_page = total_page_list[i]
        leader = leader_list[i]
        sleep_time = 1
        for page in range(1, total_page + 1):
            # print(f'total {i + 1} page {page} 开始')
            task = asyncio.create_task(self.__position_4_a_page(page, leader.leader_id, sleep_time * (page - 1)))
            tasks.append(task)
        await asyncio.wait(tasks)
        position_list = []
        for task in tasks:
            position_list.extend(task.result())
        return position_list

    async def __get_total_position_page(self, leader):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        }
        url = 'https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/lead-portfolio/trade-history'

        json_data = {
            'pageNumber': 1,
            'pageSize': 1,
            'portfolioId': leader.leader_id,
        }
        while True:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_data, headers=headers) as respond:
                    try:
                        if respond.status == 200:
                            respond_json = await respond.json()
                            total_page = int(int(respond_json['data']['total']) / 50) + 1
                            return total_page
                        else:
                            print(respond.status)
                            print(f"Retry-After={respond.headers.get('Retry-After')}")
                            print(await respond.text())
                            await asyncio.sleep(5)
                            continue
                    except Exception as e:
                        print(type(e), e)
                        print(await respond.text())
                        await asyncio.sleep(5)
                        continue

    async def __position_4_all_leader(self, leader_list, symbol):
        total_page_list = []
        for j in range(0, len(leader_list), int(len(leader_list) / 30)):
            if j + int(len(leader_list) / 30) < len(leader_list):
                leader_slice = leader_list[j:j + int(len(leader_list) / 30)]
            else:
                leader_slice = leader_list[j:]
            tasks = []
            for leader in leader_slice:
                print(f'total {leader_list.index(leader) + 1} 开始')
                task = asyncio.create_task(self.__get_total_position_page(leader))
                tasks.append(task)
            await asyncio.wait(tasks)
            for task in tasks:
                total_page_list.append(task.result())

        print(total_page_list)

        all_position_result = {}
        for leader in leader_list:
            all_position_result[leader.leader_id] = []
        start = 0
        end = 0
        start_time = time.mktime(time.localtime())
        every_time_page_amount = 200
        page_count_list = [1 for _ in range(len(total_page_list))]
        current_leader_index = 0

        loop_count = 1
        while page_count_list != total_page_list:
            if current_leader_index >= len(total_page_list)-1:
                current_leader_index = 0
            next_leader_index = (current_leader_index+
                                 min(every_time_page_amount, len(total_page_list)-current_leader_index))
            print(f'第{loop_count}次 共 {every_time_page_amount} 页 从{current_leader_index}到{next_leader_index} 开始')
            tasks = []

            while current_leader_index < next_leader_index:
                page = page_count_list[current_leader_index]
                leader = leader_list[current_leader_index]
                task = asyncio.create_task(self.__position_4_a_page(page, leader.leader_id))
                tasks.append(task)
                page_count_list[current_leader_index] += 1
                current_leader_index += 1
            await asyncio.wait(tasks)

            for task in tasks:
                leader_id = list(task.result().keys())[0]
                all_position_result[leader_id].extend(task.result()[leader_id])
            loop_count += 1
        print(f'总使用时间为{time.mktime(time.localtime()) - start_time} s')
        return all_position_result


        # while end < len(leader_list):
        #     if end == 0:
        #         page_count = 0
        #         while page_count < 1 and end < len(leader_list):
        #             page_count += total_page_list[end]
        #             end += 1
        #     else:
        #         start = end
        #         page_count = 0
        #         while page_count < 1 and end < len(leader_list):
        #             page_count += total_page_list[end]
        #             end += 1
        #     tasks = []
        #     time.sleep(3)
        #     print(f'{end - start} 个 leader 共 {page_count} 页')
        #     for i in range(start, end):
        #         task = asyncio.create_task(self.__position_4_a_leader(symbol, i, leader_list, total_page_list))
        #         tasks.append(task)
        #     await asyncio.wait(tasks)
        #     print(f'{end} 个 leader 共 {sum(total_page_list[:end])} 页 已完成！')
        #     # time.sleep(15)
        #     try:
        #         for task in tasks:
        #             result.extend(task.result())
        #     except:
        #         print(f'已进行: {sum(total_page_list[:end])}页  将重试!')  # 3921
        # print(f'总使用时间为{time.mktime(time.localtime()) - start_time} s')
        # return result

    def get_all_position_symbol(self, leader_list, symbol):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.__position_4_all_leader(leader_list, symbol))

    def get_kline_symbol(self, symbol, interval, limit, end_time=None):
        if end_time is None:
            end_time = int(time.time() * 1000)
        api_key = 'i7F6rx3Tcz6eJlSVzBc4dpV6qyszCiCOIpSz7gv9mdyq9UjVizrlu2kkmlvUIJSw'
        secret_key = 'mwU7KCworFZ17WIOqRuGaRmtwT3nnUDBhtg8HQf9CHFB7KVSxev0Rwym5mgfWjDx'
        binance = BinanceAPI('https://fapi.binance.com', api_key, secret_key)
        klines_data = []
        while limit > 1500:
            body = {
                'symbol': symbol,
                'interval': interval,
                'endTime': end_time,
                'limit': 1500,
            }
            respond = binance.api('GET', '/fapi/v1/klines', body)
            for item in respond:
                kline = {
                    'time': item[0],
                    'open': float(item[1]),
                    'high': float(item[2]),
                    'low': float(item[3]),
                    'close': float(item[4]),
                }
                klines_data.append(kline)
            end_time -= 1500 * 15 * 60 * 1000
            limit -= 1500
        else:
            body = {
                'symbol': symbol,
                'interval': interval,
                'endTime': end_time,
                'limit': limit,
            }
            respond = binance.api('GET', '/fapi/v1/klines', body)
            for item in respond:
                kline = {
                    'time': item[0],
                    'open': float(item[1]),
                    'high': float(item[2]),
                    'low': float(item[3]),
                    'close': float(item[4]),
                }
                klines_data.append(kline)
        return klines_data

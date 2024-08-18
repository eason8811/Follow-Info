import asyncio
import aiohttp
import requests_async as requests


async def main():
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
    }

    json_data = {
        'pageNumber': 2,
        'pageSize': 50,
        'portfolioId': '3972242089544603393',
    }

    url = 'https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/lead-portfolio/trade-history'
    respond = requests.post(url, headers=headers, json=json_data)
    result = await respond
    print(result.text)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    s = """
error  29 未完成
error  16 未完成
error  5 未完成
error  8 未完成
error  28 未完成
error  4 未完成
error  18 未完成
error  13 未完成
error  36 未完成
error  20 未完成
error  30 未完成
error  9 未完成
error  10 未完成
error  12 未完成
error  32 未完成
error  24 未完成
error  11 未完成
error  21 未完成
error  3 未完成
error  40 未完成
error  35 未完成
error  17 未完成
error  37 未完成
error  38 未完成
error  34 未完成
error  33 未完成
error  27 未完成
error  25 未完成
error  31 未完成
error  19 未完成
error  39 未完成
error  14 未完成
error  23 未完成
error  2 未完成
"""
    s_lst = s.strip().split('\n')
    page_list = []
    for i in s_lst:
        page = int(i.split('error  ')[1].split(' ')[0])
        page_list.append(page)
    print(sorted(page_list))

import asyncio

import aiohttp

async def main():
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 SLBrowser/9.0.0.10191 SLBChan/25',
    }
    url = 'https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/lead-portfolio/position-history'

    json_data = {
        'pageNumber': 1,
        'pageSize': 50,
        'portfolioId': '4046571179165909504',
        'sort': 'OPENING',
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json_data, headers=headers,
                                proxy='http://13.229.203.40:8080') as respond:
            print(await respond.text())

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

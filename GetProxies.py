import re
import json
import time
import requests


def get_proxies(page_amount, offset):
    result = []
    for i in range(offset, page_amount + offset):
        time.sleep(1)
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 SLBrowser/9.0.0.10191 SLBChan/25',
        }
        print(i)

        response = requests.get(f'https://www.kuaidaili.com/free/fps/{i}', headers=headers)

        regx = r"const fpsList = (.*);"
        origin_proxies_list = json.loads(re.findall(regx, response.text)[0])
        proxies_list = list(map(lambda x: {
            'http:': f'http://{x["ip"]}:{x["port"]}',
            'https:': f'https://{x["ip"]}:{x["port"]}'
        }, origin_proxies_list))
        result.extend(proxies_list)
    return result


if __name__ == '__main__':
    proxies = get_proxies(4, 3)
    print(proxies)
import requests
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP Client')
    parser.add_argument('--url', '-u', type=str, default='http://a.b.c:8090/d/e/f')
    parser.add_argument('--proxy', '-p', type=str, default='http://0.0.0.0:8080')
    args = parser.parse_args()
    proxies = {"http":args.proxy}
    response = requests.post(url=args.url, proxies=proxies, data='hello, this is http client!')
    print(f'RESPONSE: {response.text}')
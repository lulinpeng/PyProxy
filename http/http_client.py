import requests
import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP Client')
    parser.add_argument('--port', '-P', type=str)
    args = parser.parse_args()
    proxies = {"http": f"http://0.0.0.0:{args.port}"}
    response = requests.post(url='http://lu.lin.peng', proxies=proxies, data='hello, this is http client!')
    print(f'RESPONSE: {response.text}')
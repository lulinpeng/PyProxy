from flask import Flask, request, Response
import requests
import argparse

app = Flask(__name__)

ALLOWED_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']
HEADERS_TO_REMOVE = ['Host', 'Content-Length', 'Connection']

def proxy_request(url:str, method:str, headers:dict, data=None):
    print(f'proxy_request: {url} {method}')
    try:
        # remove some request headers
        cleaned_headers = {k: v for k, v in headers.items() if k not in HEADERS_TO_REMOVE}
        response = requests.request(method=method, url=url, headers=cleaned_headers, data=data,
            stream=True, allow_redirects=False, timeout=30)
        proxy_headers = dict(response.headers)
        # remove some response headers
        proxy_headers.pop('Content-Encoding', None)
        proxy_headers.pop('Transfer-Encoding', None)
        print(f'response = {response}')
        print(f'response.content = {response.content}')
        return Response(response=response.iter_content(chunk_size=8192), status=response.status_code, headers=proxy_headers)
    except requests.exceptions.RequestException as e:
        return Response(f"Proxy Error: {str(e)}", status=502)
    

@app.route('/', defaults={'path': ''}, methods=ALLOWED_METHODS) # set default path
@app.route('/<path:path>')
def proxy(path:str):
    print(f'Path = {path}')
    print(f'original request: \n{request}')
    print(f'original request headers: \n{request.headers}')
    print(f'original request data: \n{request.get_data(as_text=False)}')
    target_url = request.url.replace(request.host_url, 'http://0.0.0.0:8090/')
    print(f'target request url = {target_url}')
    data = request.get_data(as_text=False)
    return proxy_request(url=target_url, method=request.method, headers=dict(request.headers), data=data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP Proxy Server')
    parser.add_argument('--host', '-H', type=str, default='0.0.0.0',
                       help='Port to listen on (default: 0.0.0.0)')
    parser.add_argument('--port', '-P', type=int, default=8080,
                       help='Port to listen on (default: 8080)')
    args = parser.parse_args()
    print(f'host = {args.host}, port = {args.port}')
    app.run(host=args.host, port=args.port, threaded=True)
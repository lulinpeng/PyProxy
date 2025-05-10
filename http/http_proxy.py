from flask import Flask, request, Response
import requests
import argparse

app = Flask(__name__)

ALLOWED_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']
HEADERS_TO_REMOVE = ['Host', 'Content-Length', 'Connection']

@app.route('/', defaults={'path': ''}, methods=ALLOWED_METHODS) # set default path
@app.route('/<path:path>', methods=ALLOWED_METHODS)
def proxy(path:str):
    print(f'path = {path}')
    response = requests.request(
        method=request.method, url=request.url, headers=dict(request.headers), data=request.get_data(),
        params=request.args, cookies=request.cookies, allow_redirects=False, timeout=30)
    return Response(response=response.iter_content(chunk_size=8192), status=response.status_code, headers=dict(response.headers))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP Proxy Server')
    parser.add_argument('--host', '-H', type=str, default='0.0.0.0',
                       help='Port to listen on (default: 0.0.0.0)')
    parser.add_argument('--port', '-P', type=int, default=8080,
                       help='Port to listen on (default: 8080)')
    args = parser.parse_args()
    print(f'host = {args.host}, port = {args.port}')
    app.run(host=args.host, port=args.port, threaded=True)
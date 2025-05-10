from http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
import time
class RequestHandler(BaseHTTPRequestHandler):
    def _log_request(self):
        print(f"\n=== Received {self.command} Request ===")
        print(f"Path: {self.path}")
        print("Headers:")
        for k, v in self.headers.items():
            print(f"  {k}: {v}")
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length).decode('utf-8')
            print("\nBody:")
            print(body)
    def do_GET(self):
        self._log_request()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def do_POST(self):
        self._log_request()
        self.send_response(200)
        self.end_headers()
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        msg = 'OK: ' + current_time
        print(f'do_POST: msg = {msg}')
        self.wfile.write(msg.encode('utf-8'))
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP Server')
    parser.add_argument('--port', '-p', type=int, default=8000,
                       help='Port to listen on (default: 8000)')
    args = parser.parse_args()

    server_address = ('0.0.0.0', args.port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Server running on {server_address}...")
    httpd.serve_forever()
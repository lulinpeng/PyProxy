import socket
import threading
from datetime import datetime
import argparse

class ProxyServer:
    def __init__(self, host:str, port:int):
        self.host, self.port = host, port
        self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.max_pending = 5 # max length of the queue for pending connections
        return

    def start(self):
        self.proxy.bind((self.host, self.port))
        self.proxy.listen(self.max_pending) # listening
        print(f"start: proxy server start on {self.host}:{self.port}")
        while True:
            client_sock, client_address = self.proxy.accept() # waiting for client request
            print(f"start: request from {client_address} {str(datetime.now())}")
            # create thread to handle client request
            client_thread = threading.Thread(target=self.handle_client, args=(client_sock,))
            client_thread.daemon = True
            client_thread.start()
        return
    
    # get host:port from request
    def get_http_method(self, req):
        if not req:
            print(f'get_http_method: req = {req}')
            return None
        first_line = req.split('\n')[0]
        parts = first_line.split(' ') # e.g., parts=['CONNECT', 'github.githubassets.com:443', 'HTTP/1.1\r']
        print(f'get_http_method: parts = {parts}')
        if len(parts) < 3:
            return None
        return parts[0]

    def handle_client(self, client_sock):
        try:
            request = client_sock.recv(8192).decode('utf-8', errors='ignore')
            method = self.get_http_method(request)
            if method == None:
                return
            elif method == 'CONNECT':
                self.handle_https(client_sock, request)
            else:
                self.handle_http(client_sock, request)
        except Exception as e:
            print(f"handle_client: parse http/https request: {e}")

        return
    
    def get_host_port(self, req, is_https:bool = False):
        host, port = None, None
        if is_https:
            first_line = req.split('\n')[0]
            host_port = first_line.split(' ')[1]
            host, port = host_port.split(':')
            port = int(port)
        else:
            headers = req.split('\r\n')
            for header in headers:
                if header.lower().startswith('host:'):
                    host = header.split(':')[1].strip()
                    break
            port = 80 # default http port
            if ':' in host:
                host, port = host.split(':')
                port = int(port)
        print(f'get_host_port: host = {host}, port = {port}')
        return host, port
    
    def create_socket(self, host:str, port:int, timeout:int=10):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout) # 10 seconds
        sock.connect((host, port)) # 'host' is an IP address or domain name
        return sock
    
    def close_socket(self, sock):
        try:
            sock.close()
        except Exception as e:
            print(f'close socket: {str(e)}')
        return

    def handle_https(self, client_sock, request):
        try:
            host, port = self.get_host_port(request, True)
            server_sock = self.create_socket(host, port)
            client_sock.send(b'HTTP/1.1 200 Connection established\r\n\r\n') # proxy -> client
            connection_state = {'alive': True}
            
            direction =  "client -> proxy -> server"
            thread_a = threading.Thread(target=self.forward, args=(client_sock, server_sock, direction, connection_state))

            direction = "server -> proxy -> client"
            thread_b = threading.Thread(target=self.forward, args=(server_sock, client_sock, direction, connection_state))
            
            thread_a.daemon = True
            thread_b.daemon = True
            
            thread_a.start()
            thread_b.start()

            thread_a.join()
            thread_b.join()   
        except Exception as e:
            print(f"handle_https: error: {e}")
        finally:
            print('handle_https: close client socket')
            self.close_socket(client_sock)
            print('handle_https: close server socket')
            self.close_socket(server_sock)
        return
    
    def handle_http(self, client_sock, request):
        try:
            host, port = self.get_host_port(request)
            if host == None or port == None:
                print(f'handle_http: host = {host}, port = {port}')
                return

            server_sock = self.create_socket(host, port)
            server_sock.send(request.encode()) # proxy -> server
            response = server_sock.recv(4096) # proxy <- server
            while response:
                client_sock.send(response) # proxy -> client
                response = server_sock.recv(4096) # proxy <- server
        except Exception as e:
            print(f"handle_http: error: {e}")
        finally:
            print('handle_http: close client socket')
            self.close_socket(client_sock)
            print('handle_http: close server socket')
            self.close_socket(server_sock)
        return
    
    def forward(self, src_sock, dst_sock, direction:str, connection_state:dict):
        """
        send data from src_sock to dst_sock
           proxy <- src_sock
           proxy -> dst_sock
        """
        try:
            while connection_state['alive']:
                src_sock.settimeout(1)  # set a short timeout to check connection status
                try:
                    data = src_sock.recv(4096) # recv data from src_sock
                    if len(data) == 0:
                        raise Exception(f"forward: len(data) = {len(data)}, close connection")
                    dst_sock.send(data) # send data to dst_sock
                except socket.timeout:
                    continue  
        except Exception as e:
            print(f"forward: ({direction}): {e}")
        finally:
            connection_state['alive'] = False
            print('forward: close both src_sock and dst_sock')
            self.close_socket(src_sock)
            self.close_socket(dst_sock)
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='HTTP Proxy Server')
    parser.add_argument('--host', '-H', type=str, default='0.0.0.0',
                       help='Port to listen on (default: 0.0.0.0)')
    parser.add_argument('--port', '-P', type=int, default=9000,
                       help='Port to listen on (default: 9000)')
    args = parser.parse_args()
    proxy = ProxyServer(args.host, args.port)
    proxy.start()

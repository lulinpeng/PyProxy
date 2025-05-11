import socket
import threading
import ssl
from datetime import datetime
import argparse

class ProxyServer:
    def __init__(self, host:str, port:int):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.max_pending = 5 # maximum length of the queue for pending connections

    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen(self.max_pending) # listening
        print(f"proxy server start on {self.host}:{self.port}")
        while True:
            client_socket, client_address = self.server.accept()
            print(f'type(client_socket) = {type(client_socket)}')
            print(f"recv from {client_address}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
    
    def handle_client(self, client_socket):
        try:
            request = client_socket.recv(8192).decode('utf-8', errors='ignore')
            if not request:
                return
            first_line = request.split('\n')[0]
            parts = first_line.split(' ')
            print(f'handle_client: parts={parts}')
            if len(parts) < 3: # e.g., parts=['CONNECT', 'github.githubassets.com:443', 'HTTP/1.1\r']
                print(f'parts={parts}')
                return
            method, url, http_version = parts
            if method == 'CONNECT':
                self.handle_https(client_socket, request)
            else:
                self.handle_http(client_socket, request)
        except Exception as e:
            print(f"parse http/https request: {e}")
        finally:
            client_socket.close()
    
    def handle_https(self, client_socket, request):
        try:
            # get target host:port from CONNECT request
            first_line = request.split('\n')[0]
            host_port = first_line.split(' ')[1]
            host, port = host_port.split(':')
            port = int(port)
            
            print(f"build HTTPS tunnel to {host}:{port}")
            
            # connect target server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.settimeout(10) # 10 seconds
            server_socket.connect((host, port))
            
            # send a connection established response to the client
            client_socket.send(b'HTTP/1.1 200 Connection established\r\n\r\n')
            connection_state = {'alive': True}
            
            # enable bidirectional data forwarding
            client_to_server = threading.Thread(
                target=self.forward, 
                args=(client_socket, server_socket, f"client->{host}", connection_state)
            )
            server_to_client = threading.Thread(
                target=self.forward, 
                args=(server_socket, client_socket, f"{host}->client", connection_state)
            )
            
            client_to_server.daemon = True
            server_to_client.daemon = True
            
            client_to_server.start()
            server_to_client.start()
            
            client_to_server.join()
            server_to_client.join()
            
        except Exception as e:
            print(f"HTTPS error: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            try:
                server_socket.close()
            except:
                pass
    
    def handle_http(self, client_socket, request):
        try:
            headers = request.split('\r\n')
            host = None
            for header in headers:
                if header.lower().startswith('host:'):
                    host = header.split(':')[1].strip()
                    break
            if not host:
                return
            port = 80
            if ':' in host:
                host, port = host.split(':')
                port = int(port)
                
            # connect the target server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.settimeout(10)
            server_socket.connect((host, port))
            
            # forward request to the target server
            server_socket.send(request.encode())
            
            # forward response to the client
            response = server_socket.recv(4096)
            while response:
                client_socket.send(response)
                response = server_socket.recv(4096)
                
            server_socket.close()
        except Exception as e:
            print(f"HTTP error: {e}")
    
    def forward(self, source, destination, direction, connection_state):
        """forward data between two sockets"""
        try:
            while connection_state['alive']:
                source.settimeout(1)  # set a short timeout to check the connection status
                try:
                    data = source.recv(4096)
                    if len(data) == 0:
                        raise Exception("close connection")
                    destination.send(data)
                except socket.timeout:
                    continue
                    
        except Exception as e:
            print(f"forward data error: ({direction}): {e}")
        finally:
            connection_state['alive'] = False
            try:
                source.close()
            except:
                pass
            try:
                destination.close()
            except:
                pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='HTTP Proxy Server')
    parser.add_argument('--host', '-H', type=str, default='0.0.0.0',
                       help='Port to listen on (default: 0.0.0.0)')
    parser.add_argument('--port', '-P', type=int, default=9000,
                       help='Port to listen on (default: 9000)')
    args = parser.parse_args()
    proxy = ProxyServer(args.host, args.port)
    proxy.start()
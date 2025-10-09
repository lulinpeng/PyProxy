import socket
import threading
import time
import logging
import datetime
import argparse

logging.basicConfig(
    format='%(asctime)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger('UDP Hole Punching')

BUFFER_SIZE = 1024 # buffer size

class Server:
    def __init__(self, addr:tuple):
        self.clients = {}
        self.server_socket = None
        self.running = False
        self.name = 'server'
        self.addr = addr
        
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.server_socket.bind(self.addr)
        self.running = True
        logger.info(f"signaling server starts, listening {self.addr}")
        threading.Thread(target=self._listen, daemon=True).start()
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logger.info("singnaling server stop")
    
    def _listen(self):
        while self.running:
            try:
                data, addr = self.server_socket.recvfrom(BUFFER_SIZE)
                msg = data.decode().strip()
                logger.info(msg)
                if 'REGISTER' in msg:
                    client_id = msg.split(':')[0]
                    logger.info(f'{client_id} @ {addr}')
                    self.clients[client_id] = addr
                    self.server_socket.sendto(b"REGISTERED", addr)
                elif "LIST" in msg:
                    response = 'LIST:' + "\n".join([f"{cid}:{info[0]}:{info[1]}" for cid, info in self.clients.items()])
                    self.server_socket.sendto(response.encode(), addr)
                    logger.info(f"{self.name} -> {addr} client list")
                elif msg.startswith('PUNCH'):
                    starter, peer = msg.lstrip('PUNCH:').split(':')
                    logger.info(f'PUNCH starter: {client_id}, peer: {peer}')
                    self.notify_clients(starter, peer)
                else:
                    logger.info(f'UNKNOWN message: {msg}')
            except Exception as e:
                logger.error(f"server error: {e}")
    
    def notify_clients(self, peer_a:str, peer_b:str):
        addr_a = self.clients[peer_a]
        addr_b = self.clients[peer_b]
        # nofity peerA about peerB
        msg = f"PUNCH:{peer_b}"
        self.server_socket.sendto(msg.encode(), addr_a)
        # nofity peerB about peerA
        msg = f"PUNCH:{peer_a}"
        self.server_socket.sendto(msg.encode(), addr_b)
        logger.info(f"Server -> {peer_a} and {peer_b}")
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='P2P punch hole')
    parser.add_argument('--host', '-H', type=str, default='127.0.0.1',
                       help='hostname / ip address')
    parser.add_argument('--port', '-P', type=int, default=5000,
                       help='Port to listen on (default: 5000)')
    args = parser.parse_args()
    addr = (args.host, int(args.port))
    server = Server(addr)
    server.start()
    try:
        while True:
            time.sleep(5)
            print(f'server running {datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}')
    except KeyboardInterrupt:
        logger.info("exit")
        server.stop()

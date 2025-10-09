import socket
import threading
import time
import logging
import argparse

logging.basicConfig(
    format='%(asctime)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger('UDP Hole Punching')

BUFFER_SIZE = 1024 # buffer size
SERVER_ADDR = ('127.0.0.1', 5000)

class P2PClient:
    def __init__(self, name, address:tuple):
        self.register_status = False
        self.addr = address
        self.name = name
        self.peers = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.socket.bind(self.addr) # bind port
        self.running = False
        logger.info(f"{self.name} initialize, address: {self.addr}")
    
    def start(self):
        self.running = True
        # create a thread to listen
        threading.Thread(target=self.listen, daemon=True).start()
        
    def register(self):
        msg = f'{self.name}:REGISTER'
        logger.info(f"{self.name} -> server: {msg}")
        self.socket.sendto(msg.encode(), SERVER_ADDR)
        return
        
    def list_peers(self):
        msg = f'{self.name}:LIST'
        logger.info(f"{self.name} -> server: {msg}")
        self.socket.sendto(msg.encode(), SERVER_ADDR)
        return
        
    def listen(self):
        while self.running:
            try:
                data, addr = self.socket.recvfrom(BUFFER_SIZE)
                msg = data.decode()
                logger.info(f'recv {msg}', )
                if addr == SERVER_ADDR:
                    if 'REGISTERED' in msg:
                        self.register_status = True
                    elif msg.startswith('LIST'):
                        msg = msg.lstrip('LIST:')
                        infolist = [m.split(':') for m in msg.split('\n')]
                        for info in infolist:
                            self.peers[info[0]] = {'addr': (info[1], int(info[2])), 'status': False}
                        logger.info(f'LIST {self.peers}')
                    elif 'PUNCH' in msg:
                        logger.info(f'PUNCH: {msg}')
                        peername = msg.lstrip('PUNCH:')
                        msg = f'{self.name}:punchole'
                        if self.peers[peername]['status'] == False:
                            logger.info(f'{self.name} -> {peername}: {msg}')
                            client.send_message(peername, msg)
                        else:
                            msg = f'CONNECTED:{self.name}'
                            client.send_message(peername, msg)
                            
                elif msg.startswith('CONNECTED'):
                    peername = msg.split(':')[1]
                    if peername in self.peers:
                        self.peers[peername]['status'] = True
                else:
                    logger.info(f"{self.name} <- {addr}: {data.decode()}")
            except Exception as e:
                logger.error(f"{self.name} error: {e}")

    def punch_hole(self, peername:str):
        msg = f'PUNCH:{self.name}:{peername}'
        logger.info(f"{self.name} -> server -> {peername}: {msg}")
        self.socket.sendto(msg.encode(), SERVER_ADDR)
        return
    
    def send_message(self, peername:str, message:str):
        peer_addr = self.peers[peername]['addr']
        if peer_addr == self.addr:
            logger.debug('peer addr == self.addr')
            return
        self.socket.sendto(message.encode(), peer_addr)
        logger.info(f"{self.name} -> {peername}: {message}")
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='P2P punch hole')
    parser.add_argument('--name', '-N', type=str, default='anonymous',
                       help='client name')
    parser.add_argument('--host', '-H', type=str, default='127.0.0.1',
                       help='hostname / ip address')
    parser.add_argument('--port', '-P', type=int, default=9000,
                       help='Port to listen on (default: 9000)')
    args = parser.parse_args()
    # create P2P client
    addr = (args.host, int(args.port))
    client = P2PClient(args.name, addr)
    client.start()

    # register
    time.sleep(1)
    while client.register_status == False:
        logger.info(f'{args.name} registering')
        client.register()
        time.sleep(3)
    
    # wait for other peers
    while len(client.peers) <= 1:
        logger.info('wait for other peers')
        client.list_peers()
        time.sleep(3)
    
    # punch hole
    while True:
        flag = True
        for peername in client.peers.keys():
            if peername != args.name and client.peers[peername]['status'] == False:
                client.punch_hole(peername)
                client.send_message(peername, f'CONNECTED:{args.name}')
                flag = False
        if flag:
            break
        time.sleep(1)
        
    while True:
        time.sleep(3)
        logger.info(f'P2P client {args.name} running')
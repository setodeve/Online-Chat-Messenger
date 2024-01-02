import time
import json
import threading
from .inetsetting import InetSetting

class Server(InetSetting):
    def __init__(self) -> None:
        super().__init__('0.0.0.0',9001)
        self.clients = {}
        threading.Thread(target=self.receive_messages()).start()

    def receive_messages(self)-> None:
        self.sock.bind(self.setinfo)

        while True:
            try :
                message, cli_addr = self.sock.recvfrom(self.size)
                message = json.loads(message.decode('utf-8'))
                if cli_addr not in self.clients:
                    self.clients[cli_addr] = time.time()
                    if(message["message"]==(message["username"]+"-"+"reg")):
                        continue
                self.relay_message(message, cli_addr)

            except KeyboardInterrupt:
                self.close()

    def relay_message(self, message, sender):
        message = (message["username"]+" : "+message["message"]).encode('utf-8')
        for client in self.clients.keys():
            if client != sender:
                self.sock.sendto(message, client)

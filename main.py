import sys
import threading
from lib.client import Client_UDP
from lib.client import Client_TCP
from lib.server import Server_UDP
from lib.server import Server_TCP

class Main():
    def __init__(self) -> None:
        pass
    
    def start(self,args) -> None:
      if args[1] == "client":
         tcp_client = Client_TCP()
         tcp_client.client_tcp_start()
         Client_UDP(tcp_client.user_name, tcp_client.room_name, tcp_client.token)
      else:
         tcp_server = Server_TCP()
         udp_server = Server_UDP()
         t1=threading.Thread(target=tcp_server.server_tcp_start)
         t2=threading.Thread(target=udp_server.receive_messages)
         t1.start()
         t2.start()
         t1.join()
         t2.join()

if __name__ == "__main__":
   Main().start(sys.argv)

import sys
from lib.client import Client_UDP
from lib.client import Client_TCP
from lib.server import Server_UDP
from lib.server import Server_TCP

class Main():
    def __init__(self) -> None:
        pass
    
    def start() -> None:
      args = sys.argv
      if args[1] == "client":
         tcp_client = Client_TCP()
         tcp_client.client_tcp_start()
         Client_UDP(tcp_client.name,tcp_client.room_name,tcp_client.token)
      else:
         tcp_server = Server_TCP()
         tcp_server.server_tcp_start()
         Server_UDP()

if __name__ == "__main__":
   Main().start()

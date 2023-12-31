import socket
import os
import sys
from pathlib import Path
from lib.setting.udp import client
from lib.setting.udp import server
class main:
  def __init__(self) -> None:
    print('main')
  # def setting_server_tcp():
  #   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  #   server_address = '0.0.0.0'
  #   server_port = 9001

  #   dpath = 'temp'
  #   if not os.path.exists(dpath):
  #       os.makedirs(dpath)

  #   sock.bind((server_address, server_port))

  #   sock.listen(1)

  # def setting_client_tcp():
  #   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  #   server_address = '0.0.0.0'
  #   server_port = 9001

  #   try:
  #       sock.connect((server_address, server_port))
  #   except socket.error as err:
  #       print(err)
  #       sys.exit(1)


if __name__ == "__main__":
    args = sys.argv
    main()
    if args[1] == "client":
       client = client.Client()
    else:
       server = server.Server()
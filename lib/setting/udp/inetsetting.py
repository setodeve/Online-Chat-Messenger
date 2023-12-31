import sys
sys.dont_write_bytecode = True
import socket 
import os

class InetSetting:
    def __init__(self,address,port) -> None:
        self.address = address
        self.port = port
        self.setinfo = (address, port)
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        print('create socket')
        self.size = 1024

    def close(self):
        print('closing socket')
        self.sock.close()
        exit


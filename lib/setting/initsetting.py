import sys
sys.dont_write_bytecode = True
import socket 
import os

class InetSetting:
    CLIENT_OPERATION = 0
    RESPONSE_OPERATION = 1
    COMPLETE_OPERATION = 2
    POSITIVE_STATE = 1
    NEGATIVE_STATE = 2
    UNKNOWN_TOKEN = "UNKNOWN_TOKEN"

    def __init__(self,address,port) -> None:
        self.address = address
        self.port = port
        self.setinfo = (address, port)
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.size = 4096


    def close(self):
        print('closing socket')
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        exit


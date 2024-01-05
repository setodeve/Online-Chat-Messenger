import sys
sys.dont_write_bytecode = True
import socket

class InetSetting:
    CLIENT_OPERATION = 0
    RESPONSE_OPERATION = 1
    COMPLETE_OPERATION = 2
    NEW_ROOM_REQUEST_OPERATION = 1
    EXIST_ROOM_REQUEST_OPERATION = 2
    POSITIVE_STATE = 1
    NEGATIVE_STATE = 2
    UNKNOWN_TOKEN = "UNKNOWN_TOKEN"
    ERROR_CODE = {
        "PASSWORD_UNMATCH" : 0,
        "ROOM_NAME_EXIST" : 1,
        "ROOM_NAME_UNEXIST" : 2,
    }
    def __init__(self, address, port,type) -> None:
        self.address = address
        self.port = port
        self.setinfo = (address, port)
        self.sock = socket.socket(socket.AF_INET, type)
        self.size = 4096


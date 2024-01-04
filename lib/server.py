import json
import socket
import secrets
import time
from .initsetting import InetSetting

class Server_TCP(InetSetting):
    def __init__(self) -> None:
        super().__init__("0.0.0.0", 8080, socket.SOCK_STREAM)
        print("[TCP] Starting up on {} port {}".format(self.address, self.port))
        self.sock.bind(self.setinfo)
        self.sock.listen(1000)

    def server_tcp_start(self):
        while True:
            conn, cli_addr = self.sock.accept()
            try:
                while True:
                    print('[TCP]Connection from {}'.format(cli_addr))
                    message_recv = conn.recv(self.size).decode("utf-8")
                    message = json.loads(message_recv)
                    message_resp = {
                        "operation": self.RESPONSE_OPERATION,
                        "state": self.POSITIVE_STATE,
                        "payload": {
                            "user_name": message["payload"]["user_name"],
                            "room_name": message["payload"]["room_name"],
                        },
                    }
                    # ユーザー名が使用できるかチェック
                    user_name_state = self.user_name_check(message["payload"]["user_name"])
                    if user_name_state == self.POSITIVE_STATE:
                        message_resp["state"] = self.NEGATIVE_STATE
                        message_resp["payload"][
                            "error_message"
                        ] = "入力されたユーザーは使用できません。"
                        message_resp["payload"][
                            "error_code"
                        ] = self.ERROR_CODE["USER_NAME_EXIST"]
                        self.respond(message_resp,conn)
                        continue
                    self.user_add(message)
                    # ルーム名が使用できるかチェック
                    room_name_state = self.room_name_check(message["payload"]["room_name"])
                    if ((message["operation"] == 1) and (room_name_state==self.NEGATIVE_STATE) or
                        (message["operation"] == 2) and (room_name_state==self.POSITIVE_STATE)):
                        self.member_add(message,cli_addr)
                        
                        token = self.operation_check(message)
                        message_resp["payload"]["token"] = token
                        message_resp["operation"] = self.COMPLETE_OPERATION
                        self.respond(message_resp,conn)
                        break
                    elif ((message["operation"] == 1) and (room_name_state==self.POSITIVE_STATE)):
                        message_resp["operation"] = self.RESPONSE_OPERATION
                        message_resp["state"] = self.NEGATIVE_STATE
                        message_resp["payload"][
                            "error_message"
                        ] = "入力されたルーム名は使用できません。"
                        message_resp["payload"][
                            "error_code"
                        ] = self.ERROR_CODE["ROOM_NAME_EXIST"]
                        self.respond(message_resp,conn)
                        continue
                    else:
                        message_resp["state"] = self.NEGATIVE_STATE
                        message_resp["payload"][
                            "error_message"
                        ] = "入力されたルームは存在しません。"
                        message_resp["payload"][
                            "error_code"
                        ] = self.ERROR_CODE["ROOM_NAME_UNEXIST"]
                        self.respond(message_resp,conn)
                        continue
            except Exception as err:
                print('[TCP] Error: ' + str(err))
            finally:
                print('[TCP] Connection Close')
                conn.close()

    def respond(self, message_resp,conn):
        json_data = json.dumps(message_resp).encode("utf-8")
        conn.sendto(json_data, self.setinfo)

    # 新規ルームに参加 : 1
    # 既存ルームに参加 : 2
    def operation_check(self, message):
        if message["operation"] == 1:
            return self.token_create(message)
        elif message["operation"] == 2:
            return self.token_get(message["payload"]["room_name"])

    def member_add(self,message,cli_addr):
        user_name = message["payload"]["user_name"]
        room_name = message["payload"]["room_name"]
        with open("room.json", "r") as file:
            data = json.load(file)
            for i in range(len(data)):
                if data[i]["room_name"] == room_name:
                    if user_name not in data[i]["member"]:
                        data[i]["member"].append(user_name)
                        break

        with open("room.json", "w") as file:
            json.dump(data, file, indent=4)

    def user_name_check(self, user_name):
        state = self.NEGATIVE_STATE
        with open("user.json", "r") as file:
            users = json.load(file)
        for u in users:
            if u == user_name:
                state = self.POSITIVE_STATE
                break
        return state

    def room_name_check(self, room_name):
        state = self.NEGATIVE_STATE
        with open("room.json", "r") as file:
            rooms = json.load(file)
        for r in rooms:
            if r["room_name"] == room_name:
                state = self.POSITIVE_STATE
                break
        return state

    def token_get(self, room_name):
        with open("token.json", "r") as file:
            rooms = json.load(file)
        for r in rooms:
            if r["room_name"] == room_name:
                return r["token"]
        return self.UNKNOWN_TOKEN

    def token_check(self, token):
        flg = False
        with open("token.json", "r") as file:
            tokens = json.load(file)
        for t in tokens:
            if t["token"] == token:
                flg = True
                break
        return flg

    def json_rewite(self, room_name, user_name, token, file_name):
        with open(file_name, "r") as file:
            data = json.load(file)

        if file_name == "token.json":
            data.append({"room_name": room_name, "token": token})
        elif file_name == "room.json":
            data.append({"room_name": room_name, "host": user_name})
        else:
            if user_name not in data: data.append(user_name)

        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)

    def token_create(self, message):
        while True:
            token = secrets.token_hex(20)
            # 新規作成のトークンが重複していないことを確認
            if self.token_check(token) == False:
                break
        self.json_rewite(
            message["payload"]["room_name"],
            message["payload"]["user_name"],
            token,
            "token.json",
        )
        self.json_rewite(
            message["payload"]["room_name"],
            message["payload"]["user_name"],
            token,
            "room.json",
        )

        return token
    
    def user_add(self,message):
        self.json_rewite(
            "",
            message["payload"]["user_name"],
            "",
            "user.json",
        )
class Server_UDP(InetSetting):
    def __init__(self) -> None:
        super().__init__("0.0.0.0", 9001, socket.SOCK_DGRAM)
        print("[UDP] Starting up on {} port {}".format(self.address, self.port))
        self.user_name = ""
        self.room_name = ""
        self.room_info = {}
        self.client = ()
        self.clients = {}
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def receive_messages(self) -> None:
        self.sock.bind(self.setinfo)
        try:
            while True:
                message, cli_addr = self.sock.recvfrom(self.size)
                self.client = cli_addr
                if cli_addr not in self.clients:
                    self.clients[cli_addr] = time.time()

                message = json.loads(message.decode("utf-8"))
                self.user_name = message["user_name"]
                self.room_name = message["room_name"]
                print(message)
                self.set_room_info()
                self.relay_message(message,cli_addr)
        except Exception as err:
            print('[UDP] Error: ' + str(err))
        finally:
            print('[UDP] Connection Close')
            self.sock.close()
                

    def relay_message(self, message, sender):
        json_data = json.dumps(message).encode("utf-8")
        for client in self.clients.keys():
            if client != sender:
                self.sock.sendto(json_data, client)

    def set_room_info(self):
        with open("room.json", "r") as file:
            data = json.load(file)
            for i in range(len(data)):
                if data[i]["room_name"] == self.room_name:
                    self.room_info = data[i]
                    break

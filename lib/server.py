import json
import socket
import secrets
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
                            "room_name": message["payload"]["room_name"]
                        },
                    }
                    # ユーザー名が使用できるかチェック
                    user_name_state = self.user_name_check(message["payload"]["user_name"],message["payload"]["password"])
                    if user_name_state == self.NEGATIVE_STATE:
                        message_resp["state"] = self.NEGATIVE_STATE
                        message_resp["payload"][
                            "error_message"
                        ] = "パスワードが一致しません。"
                        message_resp["payload"][
                            "error_code"
                        ] = self.ERROR_CODE["PASSWORD_UNMATCH"]
                        self.respond(message_resp,conn)
                        continue
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
                break
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
        flg = False
        with open("room.json", "r") as file:
            data = json.load(file)
        for i in range(len(data)):
            if data[i]["room_name"] == room_name:
                data[i]["member"][user_name] = cli_addr
                flg = True
                break
        if flg==False:
            tmp = {
                "room_name": room_name,
                "host": user_name,
                "member": {} 
            }
            tmp["member"][user_name] = cli_addr
            data.append(tmp)

        with open("room.json", "w") as file:
            json.dump(data, file, indent=4)

    def user_name_check(self, user_name, password):
        state = self.NEGATIVE_STATE
        with open("user.json", "r") as file:
            users = json.load(file)

        if (user_name not in users) :
            users[user_name] = password
            state = self.POSITIVE_STATE
        elif (user_name in users) and users[user_name]==password:
            state = self.POSITIVE_STATE

        with open("user.json", "w") as file:
            json.dump(users, file, indent=4)
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

        return token

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
                message = json.loads(message.decode("utf-8"))
                self.user_name = message["user_name"]
                self.room_name = message["room_name"]
                self.set_room_info()
                self.clients = self.udp_address_add(message,cli_addr)
                if message["message"] == self.user_name+"registration-user-name":
                    continue
                self.relay_message(message,cli_addr)
        except Exception as err:
            print('[UDP] Error: ' + str(err))
        finally:
            print('[UDP] Connection Close')
            self.sock.close()
            self.udp_address_init()   

    def relay_message(self, message, sender):
        json_data = json.dumps(message).encode("utf-8")
        for client in self.clients:
            if client != sender:
                self.sock.sendto(json_data, tuple(client))

    def udp_address_add(self,message,cli_addr):
        user_name = message["user_name"]
        room_name = message["room_name"]
        rtn = {}
        with open("room.json", "r") as file:
            data = json.load(file)
            for i in range(len(data)):
                if data[i]["room_name"] == room_name:
                    data[i]["member"][user_name] = cli_addr
                    rtn = list(data[i]["member"].values())
                    break

        with open("room.json", "w") as file:
            json.dump(data, file, indent=4)
        return rtn

    def udp_address_init(self):
        with open("room.json", "r") as file:
            data = json.load(file)
            for i in range(len(data)):
                if "member" in data[i].keys():
                    data[i]["member"] = {}
        
        with open("room.json", "w") as file:
            json.dump(data, file, indent=4)

    def set_room_info(self):
        with open("room.json", "r") as file:
            data = json.load(file)
            for i in range(len(data)):
                if data[i]["room_name"] == self.room_name:
                    self.room_info = data[i]
                    break

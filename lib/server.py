import json
import socket
import secrets
import threading
import time
from .initsetting import InetSetting

class Server_TCP(InetSetting):
    def __init__(self) -> None:
        super().__init__("0.0.0.0", 8080, socket.SOCK_STREAM)
        print("Starting up on {} port {}".format(self.address, self.port))
        self.sock.bind(self.setinfo)
        self.sock.listen(1000)

    def server_tcp_start(self):
        while True:
            conn, cli_addr = self.sock.accept()
            try:
                message_recv = conn.recv(self.size).decode("utf-8")
                message = json.loads(message_recv)
                room_name_state = self.room_name_check(message["payload"]["room_name"])
                message_resp = {
                    "operation": self.RESPONSE_OPERATION,
                    "state": self.POSITIVE_STATE,
                    "payload": {
                        "user_name": message["payload"]["user_name"],
                        "room_name": message["payload"]["room_name"],
                    },
                }
                if room_name_state == self.POSITIVE_STATE:
                    token = self.operation_check(message)
                    message_resp["payload"]["token"] = token
                    if token == self.UNKNOWN_TOKEN:
                        message_resp["state"] = self.NEGATIVE_STATE
                        message_resp["payload"][
                            "error_message"
                        ] = "入力されたルームは存在しません。"
                    else:
                        message_resp["operation"] = self.COMPLETE_OPERATION
                    self.respond(message_resp, conn)
                    break
                else:
                    #   message_resp["operation"] = self.RESPONSE_OPERATION
                    message_resp["state"] = self.NEGATIVE_STATE
                    message_resp["payload"][
                        "error_message"
                    ] = "入力されたルーム名は使用できません。"
                    self.respond(message_resp, conn)

            except ConnectionResetError:
                break
            except AttributeError:
                break
            except BrokenPipeError:
                break
        self.sock.shutdown(socket.SHUT_RDWR)
        self.close()

    def respond(self, message_resp, conn):
        json_data = json.dumps(message_resp).encode("utf-8")
        conn.sendto(json_data, self.setinfo)

    def operation_check(self, message):
        if message["operation"] == 0:
            return self.token_create(message)
        elif message["operation"] == 2:
            return self.token_get(message["payload"]["room_name"])

    def room_name_check(self, room_name):
        state = self.POSITIVE_STATE
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
            print(r)
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
            data.append({"room_name": room_name, "host": user_name})

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

class Server_UDP(InetSetting):
    def __init__(self) -> None:
        super().__init__("0.0.0.0", 9001, socket.SOCK_DGRAM)
        self.clients = {}
        threading.Thread(target=self.receive_messages()).start()

    def receive_messages(self) -> None:
        self.sock.bind(self.setinfo)

        while True:
            try:
                message, cli_addr = self.sock.recvfrom(self.size)
                message = json.loads(message.decode("utf-8"))
                if cli_addr not in self.clients:
                    self.clients[cli_addr] = time.time()
                    if message["message"] == (message["user_name"] + "-" + "reg"):
                        continue
                self.relay_message(message, cli_addr)

            except KeyboardInterrupt:
                self.close()

    def relay_message(self, message, sender):
        message = (message["user_name"] + " : " + message["message"]).encode("utf-8")
        for client in self.clients.keys():
            if client != sender:
                self.sock.sendto(message, client)

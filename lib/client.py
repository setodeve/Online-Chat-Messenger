import json
import socket
import threading
from .initsetting import InetSetting

class Client_TCP(InetSetting):
    def __init__(self) -> None:
        super().__init__("0.0.0.0", 8080, socket.SOCK_STREAM)
        self.user_name = input("ユーザー名を入力してください : ")
        self.token = ""
        self.room_name = ""
        self.sock.connect(self.setinfo)

    def client_tcp_start(self) -> None:
        flag = False
        while True:
            data = {}
            tmp = self.room_input()
            data["operation"] = tmp["operation"]
            data["payload"] = {}
            data["payload"]["room_name"] = tmp["room_name"]
            data["payload"]["user_name"] = self.name

            json_data = json.dumps(data).encode("utf-8")
            self.sock.sendto(json_data, self.setinfo)

            message_recv = self.sock.recv(self.size).decode("utf-8")
            message = json.loads(message_recv)

            if message["state"] == self.POSITIVE_STATE:
                if message["operation"] == self.COMPLETE_OPERATION:
                    self.token = data["payload"]["token"]
                    self.room_name = data["payload"]["room_name"]
                    print(data["payload"]["room_name"] + "に参加しました。")
                else:
                    print("サポート外のケースです")
                    print(message)
                flag = True
            else:
                print(message["payload"]["error_message"])
            if flag:
                break
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except:
            pass

    def room_input(self) -> object:
        print("1または2を入力してください")
        print(" 新規ルームを作成する場合 : 1")
        print(" 既存ルームに参加する場合 : 2")
        while True:
            num = int(input())
            if num == 1:
                room_name = input("新規ルーム名を入力してください : ")
                return {"operation": 0, "room_name": room_name}
            elif num == 2:
                room_name = input("既存ルーム名を入力してください : ")
                return {"operation": 2, "room_name": room_name}
            else:
                print("1または2を入力してください")

class Client_UDP(InetSetting):
    def __init__(self,user_name, room_name, token) -> None:
        super().__init__("0.0.0.0", 9001, socket.SOCK_DGRAM)
        self.user_name = user_name
        self.token = room_name
        self.room_name = token
        threading.Thread(target=self.receive_messages).start()
        threading.Thread(target=self.send_messages).start()

        # サーバー側への疎通確認
        data = {"user_name": self.user_name, "message": self.user_name + "-" + "reg"}
        json_data = json.dumps(data).encode("utf-8")
        self.sock.sendto(json_data, self.setinfo)

    def receive_messages(self) -> None:
        while True:
            rx_meesage, addr = self.sock.recvfrom(self.size)
            print(f"{rx_meesage.decode('utf-8')}")

    def send_messages(self) -> None:
        print("メッセージを入力してください。終了するためにはendと入力してください。")
        while True:
            try:
                data = {"user_name": self.user_name, "message": input()}
                if data["message"] != "end":
                    json_data = json.dumps(data).encode("utf-8")
                    send_len = self.sock.sendto(json_data, self.setinfo)
                    print(data["user_name"] + " : " + data["message"])
                else:
                    self.close()
            except TimeoutError:
                self.close()
            except KeyboardInterrupt:
                self.close()

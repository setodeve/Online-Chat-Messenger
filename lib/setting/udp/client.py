import json
from .inetsetting import InetSetting
import threading
class Client(InetSetting):
    def __init__(self) -> None:
        super().__init__('0.0.0.0',9001)
        self.name = input("ユーザー名を入力してください : ")
        threading.Thread(target=self.receive_messages).start()
        threading.Thread(target=self.send_messages).start()

        # サーバー側への疎通確認
        data = {"username": self.name,"message": self.name+"-"+"reg"}
        json_data = json.dumps(data).encode('utf-8')
        self.sock.sendto(json_data, self.setinfo)

    def receive_messages(self)-> None:
        while True:
            rx_meesage, addr = self.sock.recvfrom(self.size)
            print(f"{rx_meesage.decode('utf-8')}")

    def send_messages(self)-> None:
      print('メッセージを入力してください。終了するためにはendと入力してください。')
      while True:
          try:
              data = {
                  "username": self.name,
                  "message": input()
              }
              if data["message"] != 'end':
                  json_data = json.dumps(data).encode('utf-8')
                  send_len = self.sock.sendto(json_data, self.setinfo)
                  print(data["username"]+" : "+data["message"])

              else:
                  self.close()
          except TimeoutError :
              self.close()
          except KeyboardInterrupt :
              self.close()



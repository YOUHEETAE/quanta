import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QAxContainer import QAxWidget

class KiwoomClient:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        try:
            self.kiwoom.OnEventConnect.connect(self._on_login)
        except AttributeError:
            print("OpenAPI 미승인 상태 - 승인 후 재실행 필요")
        print("KiwoomClient 생성됨")

    def _on_login(self, err_code):
        if err_code == 0:
            print("로그인 성공")
        else:
            print(f"로그인 실패 : {err_code}")

    def login(self):
        self.kiwoom.dynamicCall("CommConnect()")
        self.app.exec_()

if __name__ == "__main__":
    client = KiwoomClient()
    client.login()
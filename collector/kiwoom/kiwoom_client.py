import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop


class KiwoomClient:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.OnEventConnect.connect(self._on_login)
        self.login_loop = QEventLoop()

    def _on_login(self, err_code):
        if err_code == 0:
            print("로그인 성공")
        else:
            print(f"로그인 실패: {err_code}")
        self.login_loop.exit()  # 로그인 완료되면 루프 종료

    def login(self):
        self.kiwoom.dynamicCall("CommConnect()")
        self.login_loop.exec_()  # 로그인 완료까지만 대기


if __name__ == "__main__":
    client = KiwoomClient()
    client.login()
    print("로그인 완료, 다음 작업 진행 가능")

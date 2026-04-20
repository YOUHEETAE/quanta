from collector.kiwoom.kiwoom_client import KiwoomClient
from PyQt5.QtCore import QEventLoop, QTimer
from datetime import datetime
import pandas as pd
import time


class KiwoomMinuteBarFetcher:
    def __init__(self, client: KiwoomClient):
        self.client = client
        self.tr_data = []
        self.tr_loop = QEventLoop()
        self.remained_data = False
        self.error_flag = False
        self.client.kiwoom.OnReceiveTrData.connect(self._on_receive_tr)
        self.client.kiwoom.OnReceiveMsg.connect(self._on_receive_msg)

    def _on_receive_msg(self, screen_no, rqname, trcode, msg):
        print(f"메시지: {msg}")
        if "-209" in msg or "차단" in msg or "과도" in msg:
            print(f"에러 감지: {msg} → 루프 강제 종료")
            self.error_flag = True
            self.remained_data = False
            self.tr_loop.exit()

    def _on_receive_tr(self, screen_no, rqname, trcode, record_name, prev_next):
        if self.error_flag:  # 에러 상태면 무시
            return
        data = self.client.kiwoom.dynamicCall(
            "GetCommDataEx(QString, QString)", trcode, "주식분봉차트조회"
        )
        for row in data:
            self.tr_data.append(
                {
                    "date": row[2].strip()[:8],
                    "time": row[2].strip()[8:],
                    "open": row[3].strip(),
                    "high": row[4].strip(),
                    "low": row[5].strip(),
                    "close": row[0].strip(),
                    "volume": row[1].strip(),
                }
            )

        self.remained_data = prev_next == "2"
        print(
            f"수집: {len(self.tr_data)}개, 마지막: {self.tr_data[-1]['date']}, 연속: {self.remained_data}"
        )
        self.tr_loop.exit()

    def _request(self, ticker, next_val):
        self.tr_loop = QEventLoop()
        self.client.kiwoom.dynamicCall(
            "SetInputValue(QString, QString)", "종목코드", ticker
        )
        self.client.kiwoom.dynamicCall("SetInputValue(QString, QString)", "틱범위", "1")
        self.client.kiwoom.dynamicCall(
            "CommRqData(QString, QString, int, QString)",
            "분봉차트조회",
            "OPT10080",
            next_val,
            "0101",
        )
        # 30초 타임아웃
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(
            lambda: (
                setattr(self, "error_flag", True),
                setattr(self, "remained_data", False),
                self.tr_loop.exit(),
            )
        )
        timer.start(30000)
        self.tr_loop.exec_()
        timer.stop()

    def fetch(self, ticker):
        self.tr_data = []
        self.remained_data = False
        self.error_flag = False

        self._request(ticker, 0)

        while self.remained_data and not self.error_flag:
            time.sleep(1)
            self._request(ticker, 2)

        if self.error_flag:
            raise Exception(f"{ticker} 수집 중 에러 발생")

        df = pd.DataFrame(self.tr_data)
        df = df.drop_duplicates(subset=["date", "time"])
        df = df.sort_values(["date", "time"])
        return df.to_dict("records")


if __name__ == "__main__":
    client = KiwoomClient()
    client.login()
    fetcher = KiwoomMinuteBarFetcher(client)
    data = fetcher.fetch("005930")
    print(f"총 {len(data)}개")
    print(f"첫 번째: {data[0]}")
    print(f"마지막: {data[-1]}")

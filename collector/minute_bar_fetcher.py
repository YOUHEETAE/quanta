from collector.hantoo_client import HantooClient
import requests
import time
import pandas as pd
from datetime import datetime


class MinuteBarFetcher:
    def __init__(self, client: HantooClient):
        self.client = client

    def fetch(self, ticker):
        all_data = []
        hour = "153000"

        for _ in range(15):
            url = f"{self.client.base_url}/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"
            headers = {
                "authorization": f"Bearer {self.client.access_token}",
                "appkey": self.client.app_key,
                "appsecret": self.client.app_secret,
                "tr_id": "FHKST03010200",
            }
            params = {
                "FID_ETC_CLS_CODE": "",
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": ticker,
                "FID_INPUT_HOUR_1": hour,
                "FID_PW_DATA_INCU_YN": "N",
            }
            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            if data["rt_cd"] != "0":
                break

            output2 = data.get("output2", [])
            all_data.extend(output2)

            if output2:
                hour = output2[-1]["stck_cntg_hour"]  # 마지막 시간을 다음 시작점으로

            time.sleep(0.5)  # API 호출 간격

        df = pd.DataFrame(all_data)
        # 시간 기준 중복 제거
        df = df.drop_duplicates(subset=["stck_cntg_hour"])
        # 장중 시간만 필터링 (09:00 ~ 15:30)
        df = df[df["stck_cntg_hour"].between("090000", "153000")]
        # 시간순 정렬
        df = df.sort_values("stck_cntg_hour")

        return df.to_dict("records")


if __name__ == "__main__":
    client = HantooClient()
    client.get_token()
    fetcher = MinuteBarFetcher(client)
    fetcher.fetch("005930")

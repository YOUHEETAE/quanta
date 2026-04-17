from collector.hantoo_client import HantooClient
import requests

class MinuteBarFetcher:
    def __init__(self, client:HantooClient):
        self.client = client

    def fetch(self, ticker):
        url = f"{self.client.base_url}/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"
        headers = {
            "authorization": f"Bearer {self.client.access_token}",
            "appkey": self.client.app_key,
            "appsecret": self.client.app_secret,
            "tr_id": "FHKST03010200"
        }
        params = {
            "FID_ETC_CLS_CODE": "",
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": ticker,
            "FID_INPUT_HOUR_1": "153000",
            "FID_PW_DATA_INCU_YN": "Y"
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()

if __name__ == "__main__":
    client = HantooClient()
    client.get_token()
    fetcher = MinuteBarFetcher(client)
    fetcher.fetch("005930")

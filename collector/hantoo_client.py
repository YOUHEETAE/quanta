import requests
import os
from dotenv import load_dotenv

load_dotenv()

class HantooClient:
    def __init__(self):
        self.app_key = os.getenv("HANTOO_APP_KEY")
        self.app_secret = os.getenv("HANTOO_APP_SECRET")
        self.base_url = "https://openapi.koreainvestment.com:9443"
        self.access_token = None

    def get_token(self):
        url = f"{self.base_url}/oauth2/tokenP"
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }  
        response = requests.post(url, json=body)
        data = response.json()    
        if "access_token" not in data:
            raise Exception(f"토큰 발급 실패: {data}")
    
        self.access_token = data["access_token"]
        print("토큰 발급 성공")


if __name__ == "__main__":
    client = HantooClient()
    client.get_token()


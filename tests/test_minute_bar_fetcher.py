import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collector.hantoo_client import HantooClient
from collector.minute_bar_fetcher import MinuteBarFetcher

def test_fetch_single_ticker():
    client = HantooClient()
    client.get_token()
    fetcher = MinuteBarFetcher(client)
    
    data = fetcher.fetch("005930")  # 삼성전자
    
    print(data)
    assert data is not None
    assert data["rt_cd"] == "0"  # 정상처리 확인

if __name__ == "__main__":
    test_fetch_single_ticker()
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

    print(f"첫 번째: {data[0]}")
    print(f"마지막: {data[-1]}")
    hours = [d["stck_cntg_hour"] for d in data]
    print(f"전체 시간: {hours}")
    dates = set([d["stck_bsop_date"] for d in data])
    print(f"날짜 목록: {dates}")
    hours = [d["stck_cntg_hour"] for d in data]
    print(len(set(hours)))  # 고유한 시간 개수
    assert len(data) > 0


if __name__ == "__main__":
    test_fetch_single_ticker()

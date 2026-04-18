import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collector.kiwoom.kiwoom_client import KiwoomClient
from collector.kiwoom.kiwoom_minute_bar_fetcher import KiwoomMinuteBarFetcher
from datetime import datetime, timedelta
import pandas as pd


def test_fetch_single_ticker():
    client = KiwoomClient()
    client.login()

    fetcher = KiwoomMinuteBarFetcher(client)
    data = fetcher.fetch("005930")

    print(f"총 분봉 수: {len(data)}")
    print(f"첫 번째: {data[0]}")
    print(f"마지막: {data[-1]}")

    # 전체 시간 목록
    all_times = []
    t = datetime.strptime("090000", "%H%M%S")
    end = datetime.strptime("153000", "%H%M%S")
    while t <= end:
        all_times.append(t.strftime("%H%M%S"))
        t += timedelta(minutes=1)

    # 날짜별 빠진 시간 확인
    df = pd.DataFrame(data)
    total_missing = 0
    for date in sorted(df["date"].unique()):
        day_df = df[df["date"] == date]
        existing = set(day_df["time"].tolist())
        missing = [t for t in all_times if t not in existing]
        if missing:
            total_missing += len(missing)
            print(f"{date}: 빠진 시간 {len(missing)}개 → {missing[:3]}...")

    print(f"총 빠진 분봉 수: {total_missing}")
    assert len(data) > 0


if __name__ == "__main__":
    test_fetch_single_ticker()

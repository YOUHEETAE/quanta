import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from unittest.mock import MagicMock
from aggregator.volume_aggregator import VolumeAggregator
from aggregator.open_aggregator import OpenAggregator


def make_mock_store():
    # 모크 데이터 생성
    mock_data_005930 = pd.DataFrame(
        [
            {
                "date": "20260417",
                "time": "090000",
                "open": "70000",
                "high": "71000",
                "low": "69000",
                "close": "70500",
                "volume": "1000",
            },
            {
                "date": "20260417",
                "time": "090100",
                "open": "70500",
                "high": "71500",
                "low": "70000",
                "close": "71000",
                "volume": "2000",
            },
            {
                "date": "20260418",
                "time": "090000",
                "open": "71000",
                "high": "72000",
                "low": "70500",
                "close": "71500",
                "volume": "1500",
            },
            {
                "date": "20260418",
                "time": "090100",
                "open": "71500",
                "high": "72500",
                "low": "71000",
                "close": "72000",
                "volume": "2500",
            },
        ]
    )

    mock_data_000660 = pd.DataFrame(
        [
            {
                "date": "20260417",
                "time": "090000",
                "open": "50000",
                "high": "51000",
                "low": "49000",
                "close": "50500",
                "volume": "500",
            },
            {
                "date": "20260417",
                "time": "090100",
                "open": "50500",
                "high": "51500",
                "low": "50000",
                "close": "51000",
                "volume": "1500",
            },
            {
                "date": "20260418",
                "time": "090000",
                "open": "51000",
                "high": "52000",
                "low": "50500",
                "close": "51500",
                "volume": "800",
            },
            {
                "date": "20260418",
                "time": "090100",
                "open": "51500",
                "high": "52500",
                "low": "51000",
                "close": "52000",
                "volume": "1200",
            },
        ]
    )

    store = MagicMock()
    store.load_tickers.return_value = ["005930", "000660"]
    store.load.side_effect = lambda ticker: (
        mock_data_005930 if ticker == "005930" else mock_data_000660
    )
    return store


def test_volume_absolute_mean():
    store = make_mock_store()
    aggregator = VolumeAggregator(store)
    result = aggregator.absolute_mean()

    print("거래량 절대평균:")
    print(result)

    # 09:00: (1000 + 1500 + 500 + 800) / 4 = 950
    assert abs(result[result["time_label"] == "09:00"]["val"].values[0] - 950) < 0.01
    print("절대평균 검증 통과")


def test_volume_normalized_mean():
    store = make_mock_store()
    aggregator = VolumeAggregator(store)
    result = aggregator.normalized_mean()

    print("거래량 정규화평균:")
    print(result)
    assert len(result) == 2
    print("정규화평균 검증 통과")


def test_open_absolute_mean():
    store = make_mock_store()
    aggregator = OpenAggregator(store)
    result = aggregator.absolute_mean()

    print("시가 절대평균:")
    print(result)
    assert len(result) == 2
    print("시가 절대평균 검증 통과")


if __name__ == "__main__":
    test_volume_absolute_mean()
    test_volume_normalized_mean()
    test_open_absolute_mean()
    print("모든 테스트 통과")

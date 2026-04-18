import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from storage.parquet_store import ParquetStore


def test_save_and_load():
    store = ParquetStore(base_dir="storage/test_data")

    # 테스트 데이터
    data = [
        {"date": "20260417", "time": "090000", "volume": "514239"},
        {"date": "20260417", "time": "090100", "volume": "123456"},
        {"date": "20260417", "time": "090200", "volume": "789012"},
    ]

    # 저장
    store.save("005930", data)
    assert store.exists("005930")
    print("저장 성공")

    # 로드
    df = store.load("005930")
    assert df is not None
    assert len(df) == 3
    print(f"로드 성공: {len(df)}개")
    print(df.head())

    # 정리
    os.remove("storage/test_data/005930.parquet")
    os.rmdir("storage/test_data")
    print("테스트 완료")


if __name__ == "__main__":
    test_save_and_load()

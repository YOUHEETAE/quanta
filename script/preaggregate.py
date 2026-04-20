"""
로컬/자동화에서 실행: KOSPI 200 전체 집계 결과를 사전 계산하여 저장
입력: storage/data/{ticker}.parquet (개별 종목 파일)
출력: storage/data/aggregated/
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from storage.parquet_store import ParquetStore
from visualizer.indicators import get_calc_result, get_combined_results, INDICATOR_INFO

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "data")
OUTPUT_DIR = os.path.join(DATA_PATH, "aggregated")


def filter_period(df, period):
    if period == "1년":
        return df
    elif period == "20일":
        dates = sorted(df["date"].unique())[-20:]
        return df[df["date"].isin(dates)]
    elif period == "전일":
        last_date = df["date"].max()
        return df[df["date"] == last_date]
    return df


def load_all_tickers(data_path):
    store = ParquetStore(base_dir=data_path)
    ticker_names = pd.read_parquet(os.path.join(data_path, "ticker_names.parquet"))
    tickers = ticker_names["ticker"].tolist()

    dfs = []
    for ticker in tickers:
        try:
            df = store.load(ticker)
            df["ticker"] = ticker
            df["volume"] = df["volume"].astype(float).abs()
            df["open"] = df["open"].astype(float).abs()
            df["high"] = df["high"].astype(float).abs()
            df["low"] = df["low"].astype(float).abs()
            df["close"] = df["close"].astype(float).abs()
            dfs.append(df)
        except Exception as e:
            print(f"  스킵: {ticker} ({e})")

    print(f"로딩 완료: {len(dfs)}개 종목")
    df_all = pd.concat(dfs, ignore_index=True)
    df_all["time_label"] = df_all["time"].apply(lambda t: f"{t[:2]}:{t[2:4]}")
    return df_all


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("개별 종목 파일 로딩 중...")
    df = load_all_tickers(DATA_PATH)
    print(f"전체 행 수: {len(df):,}")

    periods = ["1년", "20일", "전일"]

    for period in periods:
        print(f"\n[기간: {period}] 처리 중...")
        filtered = filter_period(df, period)
        filtered = filtered[
            (filtered["time"] <= "151900")
            | (filtered["time"] == "153000")
        ]

        for indicator_key in INDICATOR_INFO.keys():
            result = get_calc_result(filtered, indicator_key)
            safe_key = indicator_key.replace(" ", "_")
            out_path = os.path.join(OUTPUT_DIR, f"kospi200_{safe_key}_{period}.parquet")
            result.to_parquet(out_path, index=False)
            print(f"  저장: kospi200_{safe_key}_{period}.parquet ({len(result)}행)")

        vol_r, vlt_r, ret_r = get_combined_results(filtered)
        for name, result in [("vol", vol_r), ("vlt", vlt_r), ("ret", ret_r)]:
            out_path = os.path.join(OUTPUT_DIR, f"kospi200_combined_{name}_{period}.parquet")
            result.to_parquet(out_path, index=False)
            print(f"  저장: kospi200_combined_{name}_{period}.parquet ({len(result)}행)")

    print(f"\n완료! {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

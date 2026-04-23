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
from visualizer.indicators import INDICATOR_INFO

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "data")
OUTPUT_DIR = os.path.join(DATA_PATH, "aggregated")

PERIODS = ["1년", "20일", "전일"]

COMBINED_KEYS = {
    "vol": "거래량 정규화평균",
    "vlt": "변동성",
    "ret": "방향성",
}


def filter_period(df, period):
    if period == "20일":
        dates = sorted(df["date"].unique())[-20:]
        return df[df["date"].isin(dates)]
    elif period == "전일":
        last_date = df["date"].max()
        return df[df["date"] == last_date]
    return df


def prepare_ticker_df(df, ticker):
    df = df.copy()
    df["ticker"] = ticker
    for col in ["volume", "open", "high", "low", "close"]:
        df[col] = df[col].astype(float).abs()
    df["time_label"] = df["time"].apply(lambda t: f"{t[:2]}:{t[2:4]}")
    return df


def compute_val(df, indicator_key):
    if indicator_key == "거래량 절대평균":
        return df.assign(val=df["volume"])
    elif indicator_key == "거래량 정규화평균":
        daily_total = df.groupby("date")["volume"].transform("sum")
        return df.assign(val=df["volume"] / daily_total * 100)
    elif indicator_key == "시가 절대평균":
        return df.assign(val=df["open"])
    elif indicator_key == "시가 정규화평균":
        first_open = (
            df[df["time"] == "090000"][["date", "open"]]
            .rename(columns={"open": "first_open"})
        )
        df = df.merge(first_open, on="date", how="left").dropna(subset=["first_open"])
        return df.assign(val=(df["open"] / df["first_open"] - 1) * 100)
    elif indicator_key == "변동성":
        return df.assign(val=(df["high"] - df["low"]) / df["open"] * 100)
    elif indicator_key == "방향성":
        return df.assign(val=(df["close"] - df["open"]) / df["open"] * 100)
    elif indicator_key == "위치":
        return df.assign(val=(df["close"] - df["low"]) / (df["high"] - df["low"]))
    raise ValueError(f"Unknown indicator: {indicator_key}")


def update_accumulator(acc, df_with_val):
    df = df_with_val[["time_label", "val"]].replace(
        [float("inf"), float("-inf")], float("nan")
    ).dropna(subset=["val"])
    for time_label, group in df.groupby("time_label")["val"]:
        if time_label not in acc:
            acc[time_label] = [0.0, 0]
        acc[time_label][0] += group.sum()
        acc[time_label][1] += len(group)


def finalize(acc):
    rows = [
        {"time_label": tl, "val": s / c if c > 0 else float("nan")}
        for tl, (s, c) in acc.items()
    ]
    return pd.DataFrame(rows).sort_values("time_label").reset_index(drop=True)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    store = ParquetStore(base_dir=DATA_PATH)
    ticker_names = pd.read_parquet(os.path.join(DATA_PATH, "ticker_names.parquet"))
    tickers = ticker_names["ticker"].tolist()
    print(f"종목 수: {len(tickers)}")

    all_indicator_keys = list(INDICATOR_INFO.keys())

    for period in PERIODS:
        print(f"\n[기간: {period}]")

        accs = {k: {} for k in all_indicator_keys}

        for i, ticker in enumerate(tickers):
            try:
                df = store.load(ticker)
                if df is None:
                    continue
                df = prepare_ticker_df(df, ticker)
                df = filter_period(df, period)
                df = df[(df["time"] <= "151900") | (df["time"] == "153000")]
                if df.empty:
                    continue

                for key in all_indicator_keys:
                    df_val = compute_val(df, key)
                    update_accumulator(accs[key], df_val)

                if (i + 1) % 50 == 0:
                    print(f"  {i+1}/{len(tickers)} 처리 중...")

            except Exception as e:
                print(f"  스킵: {ticker} ({e})")

        for key in all_indicator_keys:
            result = finalize(accs[key])
            safe_key = key.replace(" ", "_")
            out_path = os.path.join(OUTPUT_DIR, f"kospi200_{safe_key}_{period}.parquet")
            result.to_parquet(out_path, index=False)
            print(f"  저장: kospi200_{safe_key}_{period}.parquet ({len(result)}행)")

        for name, key in COMBINED_KEYS.items():
            result = finalize(accs[key])
            out_path = os.path.join(OUTPUT_DIR, f"kospi200_combined_{name}_{period}.parquet")
            result.to_parquet(out_path, index=False)
            print(f"  저장: kospi200_combined_{name}_{period}.parquet ({len(result)}행)")

    print(f"\n완료! {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

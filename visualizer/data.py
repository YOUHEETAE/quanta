import os
import streamlit as st
import pandas as pd
from storage.parquet_store import ParquetStore


def _ensure_data(path):
    aggregated_dir = os.path.join(path, "aggregated")
    has_data = os.path.exists(aggregated_dir) and any(
        f.endswith(".parquet") for f in os.listdir(aggregated_dir)
    )
    if not has_data:
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id="youheetae/quanta-data",
            repo_type="dataset",
            local_dir=path,
            token=st.secrets["HF_TOKEN"],
        )


def get_data_path():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "storage/data")


@st.cache_data
def load_ticker_store(path):
    return ParquetStore(base_dir=path)


@st.cache_data
def load_ticker_names(data_path):
    return pd.read_parquet(os.path.join(data_path, "ticker_names.parquet"))


@st.cache_data
def load_ticker_df(_store, ticker):
    df = _store.load(ticker)
    df["ticker"] = ticker
    df["volume"] = df["volume"].astype(float).abs()
    df["open"] = df["open"].astype(float).abs()
    df["high"] = df["high"].astype(float).abs()
    df["low"] = df["low"].astype(float).abs()
    df["close"] = df["close"].astype(float).abs()
    df["time_label"] = df["time"].apply(lambda t: f"{t[:2]}:{t[2:4]}")
    return df


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


@st.cache_data
def load_kospi200_indicator(data_path, indicator, period):
    safe_key = indicator.replace(" ", "_")
    path = os.path.join(data_path, "aggregated", f"kospi200_{safe_key}_{period}.parquet")
    return pd.read_parquet(path)


@st.cache_data
def load_kospi200_combined(data_path, period):
    agg = os.path.join(data_path, "aggregated")
    vol_r = pd.read_parquet(os.path.join(agg, f"kospi200_combined_vol_{period}.parquet"))
    vlt_r = pd.read_parquet(os.path.join(agg, f"kospi200_combined_vlt_{period}.parquet"))
    ret_r = pd.read_parquet(os.path.join(agg, f"kospi200_combined_ret_{period}.parquet"))
    return vol_r, vlt_r, ret_r

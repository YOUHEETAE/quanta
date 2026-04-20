import os
import streamlit as st
import pandas as pd
from storage.parquet_store import ParquetStore


def _ensure_data(path):
    has_data = os.path.exists(path) and any(
        f.endswith(".parquet") for f in os.listdir(path)
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
def load_data(path):
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
def load_combined(data_path, period):
    df = pd.read_parquet(os.path.join(data_path, "combined.parquet"))
    df["volume"] = df["volume"].astype(float).abs()
    df["open"] = df["open"].astype(float).abs()
    df["high"] = df["high"].astype(float).abs()
    df["low"] = df["low"].astype(float).abs()
    df["close"] = df["close"].astype(float).abs()
    df["time_label"] = df["time"].apply(lambda t: f"{t[:2]}:{t[2:4]}")
    df = filter_period(df, period)
    df = df[(df["time"] <= "151900") | (df["time"] == "153000")]
    return df

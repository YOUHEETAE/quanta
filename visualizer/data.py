import os
import streamlit as st
import pandas as pd
from storage.parquet_store import ParquetStore


@st.cache_data
def load_data():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "storage/data")
    return ParquetStore(base_dir=path)


@st.cache_data
def load_ticker_names():
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "storage/data/ticker_names.parquet",
    )
    return pd.read_parquet(path)


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
def load_combined(_store, period):
    tickers = _store.load_tickers()
    all_df = []
    for ticker in tickers:
        df = load_ticker_df(_store, ticker)
        df = filter_period(df, period)
        df = df[(df["time"] <= "151900") | (df["time"] == "153000")]
        all_df.append(df)
    return pd.concat(all_df)

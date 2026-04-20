import pandas as pd
from storage.parquet_store import ParquetStore


class BaseAggregator:
    def __init__(self, store: ParquetStore, column: str):
        self.store = store
        self.column = column

    def _load_all(self):
        tickers = self.store.load_tickers()
        all_df = []
        for ticker in tickers:
            df = self.store.load(ticker)
            if df is None:
                continue
            df["ticker"] = ticker
            df[self.column] = df[self.column].astype(float)
            df["time_label"] = df["time"].apply(lambda t: f"{t[:2]}:{t[2:4]}")
            all_df.append(df)
        return pd.concat(all_df)

    @staticmethod
    def calc_absolute_mean(df, column):
        return (
            df.groupby("time_label")[column]
            .mean()
            .reset_index()
            .rename(columns={column: "val"})
        )

    @staticmethod
    def calc_normalized_mean(df, column):
        df = df.copy()
        df["daily_total"] = df.groupby(["ticker", "date"])[column].transform("sum")
        df["val"] = (df[column] / df["daily_total"]) * 100
        return df.groupby("time_label")["val"].mean().reset_index()

    def absolute_mean(self):
        return self.calc_absolute_mean(self._load_all(), self.column)

    def normalized_mean(self):
        return self.calc_normalized_mean(self._load_all(), self.column)

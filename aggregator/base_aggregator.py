# aggregator/base_aggregator.py
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
            all_df.append(df)
        return pd.concat(all_df)

    def absolute_mean(self):
        df = self._load_all()
        return df.groupby("time")[self.column].mean().reset_index()

    def normalized_mean(self):
        df = self._load_all()
        df["daily_total"] = df.groupby(["ticker", "date"])[self.column].transform("sum")
        df[f"norm_{self.column}"] = df[self.column] / df["daily_total"]
        return df.groupby("time")[f"norm_{self.column}"].mean().reset_index()

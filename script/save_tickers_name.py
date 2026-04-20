import sys

sys.path.append(".")

import FinanceDataReader as fdr
import pandas as pd
from storage.parquet_store import ParquetStore

store = ParquetStore()
tickers = store.load_tickers()

kospi = fdr.StockListing("KOSPI")
kospi = kospi[["Code", "Name"]].rename(columns={"Code": "ticker", "Name": "name"})

df = pd.DataFrame({"ticker": tickers})
df = df.merge(kospi, on="ticker", how="left")
df["name"] = df["name"].fillna(df["ticker"])

path = "storage/data/ticker_names.parquet"
df.to_parquet(path, index=False)
print(df.head(10))
print(f"저장 완료: {len(df)}개")

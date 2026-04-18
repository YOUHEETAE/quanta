import pandas as pd
import os


class ParquetStore:
    def __init__(self, base_dir="storage/data"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def save(self, ticker, data):
        df = pd.DataFrame(data)
        path = f"{self.base_dir}/{ticker}.parquet"
        df.to_parquet(path, index=False)
        print(f"저장 완료: {path} ({len(df)}개)")

    def load(self, ticker):
        path = f"{self.base_dir}/{ticker}.parquet"
        if not os.path.exists(path):
            return None
        return pd.read_parquet(path)

    def save_tickers(self, tickers):
        df = pd.DataFrame({"ticker": tickers})
        path = f"{self.base_dir}/tickers.parquet"
        df.to_parquet(path, index=False)
        print(f"종목코드 저장 완료: {len(tickers)}개")

    def load_tickers(self):
        path = f"{self.base_dir}/tickers.parquet"
        if not os.path.exists(path):
            return None
        return pd.read_parquet(path)["ticker"].tolist()

    def exists(self, ticker):
        return os.path.exists(f"{self.base_dir}/{ticker}.parquet")

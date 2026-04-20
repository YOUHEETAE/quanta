import pandas as pd
import os


class ParquetStore:
    def __init__(self, base_dir="storage/data"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def save(self, ticker, data):
        df = pd.DataFrame(data)
        tmp_path = f"{self.base_dir}/{ticker}.tmp.parquet"
        final_path = f"{self.base_dir}/{ticker}.parquet"
        df.to_parquet(tmp_path, index=False)
        os.replace(tmp_path, final_path)  # 원자적 rename
        print(f"저장 완료: {final_path} ({len(df)}개)")

    def load(self, ticker):
        path = f"{self.base_dir}/{ticker}.parquet"
        if not os.path.exists(path):
            return None
        return pd.read_parquet(path)

    def exists(self, ticker):
        final_path = f"{self.base_dir}/{ticker}.parquet"
        tmp_path = f"{self.base_dir}/{ticker}.tmp.parquet"
        # tmp 파일 있으면 불완전한 데이터 → 재수집
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            return False
        return os.path.exists(final_path)

    def update(self, ticker, new_data):
        df_new = pd.DataFrame(new_data)
        existing = self.load(ticker)
        if existing is not None:
            df_merged = pd.concat([existing, df_new], ignore_index=True)
            df_merged = df_merged.drop_duplicates(subset=["date", "time"])
            df_merged = df_merged.sort_values(["date", "time"]).reset_index(drop=True)
        else:
            df_merged = df_new
        self.save(ticker, df_merged.to_dict("records"))

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

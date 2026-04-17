import FinanceDataReader as fdr

class Kospi200Fetcher:
    def get_tickers(self):
        df = fdr.StockListing('KOSPI')
        df = df.sort_values('Marcap', ascending=False).head(200)
        tickers = df['Code'].tolist()
        return tickers

if __name__ == "__main__":
    fetcher = Kospi200Fetcher()
    tickers = fetcher.get_tickers()
    print(tickers)
    print(f"총 종목 수: {len(tickers)}")
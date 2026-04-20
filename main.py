import sys
import os
import time
import logging

sys.path.append(".")

from collector.kospi200_fetcher import Kospi200Fetcher
from collector.kiwoom.kiwoom_client import KiwoomClient
from collector.kiwoom.kiwoom_minute_bar_fetcher import KiwoomMinuteBarFetcher
from storage.parquet_store import ParquetStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("storage/collect.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def main():
    client = KiwoomClient()
    client.login()

    tickers = Kospi200Fetcher().get_tickers()
    store = ParquetStore()
    store.save_tickers(tickers)
    fetcher = KiwoomMinuteBarFetcher(client)

    logger.info(f"총 {len(tickers)}개 종목 수집 시작")

    for i, ticker in enumerate(tickers):
        try:
            if store.exists(ticker):
                existing = store.load(ticker)
                since_date = existing["date"].max()
                logger.info(f"[{i+1}/{len(tickers)}] {ticker} 증분 수집 (since {since_date})")
                data = fetcher.fetch(ticker, since_date=since_date)
                if not data:
                    logger.info(f"→ {ticker} 새 데이터 없음, 스킵")
                    continue
                store.update(ticker, data)
                logger.info(f"→ {ticker} 업데이트 완료 (+{len(data)}개)")
            else:
                logger.info(f"[{i+1}/{len(tickers)}] {ticker} 신규 수집 중...")
                data = fetcher.fetch(ticker)
                if not data:
                    logger.warning(f"→ {ticker} 데이터 없음, 스킵")
                    continue
                store.save(ticker, data)
                logger.info(f"→ {ticker} 저장 완료 ({len(data)}개)")
            time.sleep(3)

        except Exception as e:
            logger.error(f"→ {ticker} 에러 발생: {e}, 스킵")
            time.sleep(10)
            continue

    logger.info("전체 수집 완료")


if __name__ == "__main__":
    main()

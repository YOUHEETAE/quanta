import sys
import os
import logging

sys.path.append(".")

from collector.kospi200_fetcher import Kospi200Fetcher
from collector.kiwoom.kiwoom_client import KiwoomClient
from collector.kiwoom.kiwoom_minute_bar_fetcher import KiwoomMinuteBarFetcher
from storage.parquet_store import ParquetStore

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("storage/collect.log", encoding="utf-8"),
        logging.StreamHandler(),  # 터미널에도 출력
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
        if store.exists(ticker):
            logger.info(f"[{i+1}/{len(tickers)}] {ticker} 이미 존재, 스킵")
            continue
        try:
            logger.info(f"[{i+1}/{len(tickers)}] {ticker} 수집 중...")
            data = fetcher.fetch(ticker)

            if not data:
                logger.warning(f"→ {ticker} 데이터 없음, 스킵")
                continue

            store.save(ticker, data)
            logger.info(f"→ {ticker} 저장 완료 ({len(data)}개)")

        except Exception as e:
            logger.error(f"→ {ticker} 에러 발생: {e}, 스킵")
            if store.exists(ticker):
                os.remove(f"storage/data/{ticker}.parquet")
            continue

    logger.info("전체 수집 완료")


if __name__ == "__main__":
    main()

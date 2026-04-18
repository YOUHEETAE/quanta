# Quanta

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active%20Development-orange?style=flat-square)

> Extracts structural intraday liquidity patterns across the entire KOSPI 200 universe.  
> Aggregates 1-minute candlestick data across 200 stocks × 249 trading days  
> to extract statistically meaningful buy/sell timing signals.

---

## Overview

KOSPI 200 편입 종목의 1년치 분봉 데이터를 수집·집계하여,  
장중 시간대별 평균 거래량·가격 패턴을 도출하는 분석 엔진.

```
수집   200 종목 × 249 거래일 × ~380 분봉 ≈ ~19M rows
       (동시호가 구간 15:20~15:29 제외, 키움 특성상 미제공)
집계   절대평균 / 정규화평균 (거래량, 시가, 고가, 저가, 종가)
출력   장중 09:00 ~ 15:30 패턴 그래프
```

This allows detection of abnormal volume concentration  
relative to historical intraday baselines.

---

## Research Question

> *"KOSPI 200 전체 종목을 1년간 집계했을 때,  
> 장중 어느 시간대에 거래가 집중되는가?"*

단일 종목 또는 단기 관찰의 노이즈를 제거하고,  
200개 종목 × 1년치 데이터의 집합적 패턴에서 구조적 신호를 탐색한다.

---

## Methodology

### 1. 절대평균 (Absolute Mean)

종목·거래일 구분 없이 특정 분(minute)의 값을 단순 합산 후 평균.

```
AbsMean(t) = Σ Value(stock_i, day_j, time_t) / N

where N = number of valid observations at time t
```

대형주 거래량이 전체 평균을 지배하는 특성을 그대로 반영.  
시장 전체의 실제 자금 흐름 규모를 나타낸다.

### 2. 정규화평균 (Normalized Mean)

각 종목·거래일의 하루 총합 대비 분봉 비율로 정규화 후 평균.

```
NormVal(stock_i, day_j, time_t) = Value(stock_i, day_j, time_t) / DailyTotal(stock_i, day_j)
NormMean(t) = Σ NormVal(stock_i, day_j, time_t) / N

where N = number of valid observations at time t
```

종목 간 스케일 차이를 제거하여 순수한 시간대별 패턴을 추출한다.  
This removes cross-sectional scale differences between stocks.

All minute bars are aligned to a fixed time index (09:00–15:30),
and missing values are excluded. N represents the number of valid observations at each time point.

---

## Architecture

```
quanta/
├── collector/
│   ├── kiwoom/
│   │   ├── kiwoom_client.py             # 키움 OpenAPI+ 로그인 (32bit COM)
│   │   └── kiwoom_minute_bar_fetcher.py # 과거 1년치 분봉 수집 (OPT10080)
│   ├── hantoo/
│   │   ├── hantoo_client.py             # 한국투자증권 REST API 인증
│   │   └── minute_bar_fetcher.py        # 매일 당일 분봉 수집
│   └── kospi200_fetcher.py              # KOSPI 200 종목 리스트 수집
│
├── storage/
│   ├── data/
│   │   ├── raw/                         # 종목별 원본 Parquet
│   │   └── processed/                   # 집계 결과 Parquet
│   └── parquet_store.py                 # 저장/로드/append
│
├── aggregator/
│   ├── base_aggregator.py               # 공통 집계 베이스 클래스
│   ├── volume_aggregator.py             # 거래량 집계
│   ├── open_aggregator.py               # 시가 집계
│   ├── high_aggregator.py               # 고가 집계
│   ├── low_aggregator.py                # 저가 집계
│   └── close_aggregator.py              # 종가 집계
│
├── visualizer/
│   └── volume_chart.py                  # 장중 패턴 시각화
│
├── docs/
│   └── requirements_v02.pdf             # 요구사항 정의서
│
├── main.py
└── README.md
```

---

## Data Pipeline

```
[FinanceDataReader]              KOSPI 200 종목 리스트 수집 → tickers.parquet
    ↓
[키움 OPT10080 TR]              200 종목 × 1년치 분봉 초기 적재 (32bit / Windows)
    ↓                           (연속 조회, 약 50분 소요)
[storage/data/raw/]             종목별 Parquet 저장 (date, time, open, high, low, close, volume)
    ↓
[한투 REST API]                 매일 15:30 당일 분봉 증분 수집 (GitHub Actions)
    ↓
[BaseAggregator]                거래량 / 시가 / 고가 / 저가 / 종가 절대평균·정규화평균 집계
    ↓
[storage/data/processed/]       집계 결과 저장
    ↓
[Plotly]                        장중 패턴 그래프 → Streamlit Cloud 배포
```

---

## Requirements

### 초기 적재 (키움 / Windows 전용)

```
Windows 10/11
Python 3.9 32bit (venv32)
키움증권 계좌 및 OpenAPI+ 신청 완료
```

```bash
pip install PyQt5 pandas fastparquet finance-datareader
```

### 매일 배치 / 집계 / 시각화

```
Python 3.10+
한국투자증권 계좌 및 OpenAPI 신청 완료
```

```bash
pip install pandas numpy plotly streamlit finance-datareader fastparquet requests python-dotenv
```

---

## Constraints

| 항목 | 내용 |
|------|------|
| 초기 적재 환경 | Windows 전용 (키움 COM API / 32bit Python) |
| 매일 배치 환경 | GitHub Actions (Ubuntu) / 한투 REST API |
| 데이터 규모 | 200 × 249 × ~380 ≈ ~19M rows |
| 동시호가 구간 | 15:20~15:29 거래량 0 분봉은 키움이 제외하여 제공 (정상) |
| 분봉 제공 범위 | 키움 실계좌 기준 약 1년치 제공 확인 |

---

## Roadmap

- [x] Phase 1 — 환경 구축 (키움 32bit venv32 / 한투 REST 환경 분리)
- [x] Phase 2 — KOSPI 200 전 종목 1년치 분봉 초기 적재 (키움 OPT10080)
- [x] Phase 3 — 거래량·시가·고가·저가·종가 절대평균 / 정규화평균 집계
- [ ] Phase 4 — 장중 패턴 시각화 (Plotly 그래프)
- [ ] Phase 5 — GitHub Actions 배치 + Streamlit Cloud 배포
- [ ] Phase 6 — 매수/매도 타이밍 신호 도출

---

## Documents

| 문서 | 링크 |
|------|------|
| 요구사항 정의서 (PDF) | [docs/requirements_v02.pdf](docs/requirements_v02.pdf) |

---

## License

MIT
# Quanta

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-In%20Development-orange?style=flat-square)

> Intraday volume pattern analysis engine for KOSPI 200 constituents.  
> Aggregates 1-minute candlestick data across 200 stocks × 240 trading days  
> to extract statistically meaningful buy/sell timing signals.

---

## Overview

KOSPI 200 편입 종목의 1년치 분봉 거래량 데이터를 수집·집계하여,  
장중 시간대별 평균 거래량 패턴을 도출하는 분석 엔진.

```
수집   200 종목 × 240 거래일 × 390 분봉 ≈ 18,720,000 rows
집계   절대평균 / 정규화평균 (종목 간 스케일 차이 제거)
출력   장중 09:00 ~ 15:30 거래량 패턴 그래프
```

향후 가격 데이터(고점·저점)를 추가하여 매수/매도 타이밍 모델로 확장 예정.

---

## Research Question

> *"KOSPI 200 전체 종목을 1년간 집계했을 때,  
> 장중 어느 시간대에 거래가 집중되는가?"*

단일 종목 또는 단기 관찰의 노이즈를 제거하고,  
200개 종목 × 1년치 데이터의 집합적 패턴에서 구조적 신호를 탐색한다.

---

## Methodology

### 1. 절대평균 (Absolute Mean)

종목·거래일 구분 없이 특정 분(minute)의 거래량을 단순 합산 후 평균.

```
AbsMean(t) = Σ Volume(stock_i, day_j, time_t) / (200 × 240)
```

대형주 거래량이 전체 평균을 지배하는 특성을 그대로 반영.  
시장 전체의 실제 자금 흐름 규모를 나타낸다.

### 2. 정규화평균 (Normalized Mean)

각 종목·거래일의 하루 총거래량 대비 분봉 비율로 정규화 후 평균.

```
NormVol(stock_i, day_j, time_t) = Volume(stock_i, day_j, time_t) / DailyTotal(stock_i, day_j)
NormMean(t) = Σ NormVol(stock_i, day_j, time_t) / (200 × 240)
```

종목 간 거래량 스케일 차이를 제거하여 순수한 시간대별 패턴을 추출.  
소형주와 대형주를 동등한 가중치로 반영한다.

---

## Architecture

```
quanta/
├── collector/
│   ├── kiwoom_client.py       # 키움증권 OpenAPI+ COM 인터페이스
│   ├── kospi200_fetcher.py    # KOSPI 200 종목 리스트 수집 (pykrx)
│   └── minute_bar_fetcher.py  # 분봉 데이터 수집 (OPT10080 TR)
│
├── storage/
│   └── parquet_store.py       # 종목별 Parquet 저장/로드
│
├── aggregator/
│   ├── absolute_mean.py       # 절대평균 계산
│   └── normalized_mean.py     # 정규화평균 계산
│
├── visualizer/
│   └── volume_chart.py        # 장중 거래량 패턴 시각화
│
├── docs/
│   ├── requirements.docx      # 요구사항 정의서
│   └── requirements.pdf       # 요구사항 정의서 (PDF)
│
├── main.py
└── README.md
```

---

## Data Pipeline

```
[pykrx]                         KOSPI 200 종목 리스트 수집
    ↓
[키움 OPT10080 TR]              200 종목 × 1년치 분봉 수집
    ↓                           (3.6초/건 rate limit 준수, ~12분 소요)
[Parquet]                       종목별 로컬 저장
    ↓                           (예상 용량 500MB ~ 1GB)
[pandas / numpy]                절대평균 / 정규화평균 집계
    ↓
[plotly / matplotlib]           장중 거래량 패턴 그래프 출력
```

---

## Requirements

```
Windows 10/11       키움증권 OpenAPI+ COM 방식 (Windows 전용)
Python 3.10+
키움증권 계좌 및 OpenAPI+ 신청 완료
```

```bash
pip install pykrx pyarrow pandas numpy plotly PyQt5
```

---

## Constraints

| 항목 | 내용 |
|------|------|
| 실행 환경 | Windows 전용 (키움 COM API) |
| 분봉 제공 범위 | 키움 OPT10080 과거 데이터 제공 범위에 따라 수집 기간 상이할 수 있음 |
| 데이터 규모 | 200 × 240 × 390 ≈ 1,872만 row |
| API 호출 제한 | TR 요청 3.6초/건, 전체 수집 약 12분 소요 |
| 송금 처리 | 오픈뱅킹 미연동, 실서비스 전환 시 별도 연동 필요 |

---

## Roadmap

- [ ] Phase 1 — 환경 구축 및 파일럿 수집 (5~10개 종목 테스트)
- [ ] Phase 2 — KOSPI 200 전 종목 1년치 분봉 수집
- [ ] Phase 3 — 절대평균 / 정규화평균 집계
- [ ] Phase 4 — 장중 거래량 패턴 시각화 (그래프 2개)
- [ ] Phase 5 — 가격 데이터 추가 (고점·저점 평균)
- [ ] Phase 6 — 매수/매도 타이밍 신호 도출

---

## Documents

| 문서 | 링크 |
|------|------|
| 요구사항 정의서 (PDF)  | [docs/requirements.pdf](docs/requirements_v02.pdf) |

---

## License

MIT
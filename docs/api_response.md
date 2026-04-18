# 한투 API 응답 구조

## 엔드포인트
GET /uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice

## output1 (딕셔너리 - 하루 요약)

| 필드 | 설명 | 예시 |
|------|------|------|
| hts_kor_isnm | 종목명 | 삼성전자 |
| stck_prpr | 현재가 | 216500 |
| stck_prdy_clpr | 전일 종가 | 217500 |
| prdy_vrss | 전일 대비 | -1000 |
| prdy_ctrt | 전일 대비율 | -0.46 |
| acml_vol | 누적 거래량 | 12213959 |
| acml_tr_pbmn | 누적 거래대금 | 2645192690250 |

## output2 (리스트 - 분봉 데이터)

| 필드 | 설명 | 예시 |
|------|------|------|
| stck_bsop_date | 거래일 | 20260417 |
| stck_cntg_hour | 시간 | 153000 |
| stck_prpr | 현재가 | 216500 |
| stck_oprc | 시가 | 216500 |
| stck_hgpr | 고가 | 216750 |
| stck_lwpr | 저가 | 216500 |
| cntg_vol | 거래량 ← Phase 1 핵심 | 528 |
| acml_tr_pbmn | 누적 거래대금 | 2645192690250 |

## 사용 필드

| Phase | 필드 | 용도 |
|-------|------|------|
| Phase 1 | cntg_vol | 분봉 거래량 집계 |
| Phase 2 | stck_hgpr | 장중 평균 고점 |
| Phase 2 | stck_lwpr | 장중 평균 저점 |

## 응답 코드

| rt_cd | 설명 |
|-------|------|
| 0 | 정상처리 |
| 그 외 | 오류 |
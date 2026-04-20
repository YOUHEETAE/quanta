import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from data import (
    load_ticker_store, load_ticker_names, load_ticker_df,
    load_kospi200_indicator, load_kospi200_combined,
    filter_period, get_data_path, _ensure_data,
)
from indicators import INDICATOR_INFO, get_calc_result, get_combined_results
from charts import draw_single, draw_combined

data_path = get_data_path()
with st.spinner("데이터 다운로드 중... (최초 1회, 약 1~2분 소요)"):
    _ensure_data(data_path)

store = load_ticker_store(data_path)
ticker_names = load_ticker_names(data_path)

st.sidebar.title("Quanta")
mode = st.sidebar.radio("모드", ["전체 KOSPI 200", "개별 종목"])
view = st.sidebar.radio("보기", ["개별 지표", "통합 뷰"])
period = st.sidebar.radio("기간", ["1년", "20일", "전일"])

if view == "개별 지표":
    indicator = st.sidebar.selectbox(
        "지표",
        list(INDICATOR_INFO.keys()),
        format_func=lambda x: INDICATOR_INFO[x]["label"],
    )

st.title("KOSPI 200 장중 패턴 분석")

if mode == "전체 KOSPI 200":
    if view == "개별 지표":
        result = load_kospi200_indicator(data_path, indicator, period)
        fig = draw_single(
            result,
            f"KOSPI 200 {INDICATOR_INFO[indicator]['label']} ({period})",
            indicator,
        )
        st.plotly_chart(fig, width="stretch")
    else:
        vol_r, vlt_r, ret_r = load_kospi200_combined(data_path, period)
        fig = draw_combined(vol_r, vlt_r, ret_r, f"KOSPI 200 통합 뷰 ({period})")
        st.plotly_chart(fig, width="stretch")

else:
    options = ticker_names["name"] + " (" + ticker_names["ticker"] + ")"
    selected = st.selectbox("종목 선택", options)
    ticker = re.search(r"\((\d{6})\)$", selected).group(1)

    with st.spinner("데이터 로딩 중..."):
        df = load_ticker_df(store, ticker)
        df = filter_period(df, period)
        df = df[(df["time"] <= "151900") | (df["time"] == "153000")]

    if view == "개별 지표":
        result = get_calc_result(df, indicator)
        fig = draw_single(
            result,
            f"{ticker} {INDICATOR_INFO[indicator]['label']} ({period})",
            indicator,
        )
        st.plotly_chart(fig, width="stretch")
    else:
        vol_r, vlt_r, ret_r = get_combined_results(df)
        fig = draw_combined(vol_r, vlt_r, ret_r, f"{ticker} 통합 뷰 ({period})")
        st.plotly_chart(fig, width="stretch")

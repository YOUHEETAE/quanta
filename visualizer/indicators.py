import pandas as pd
from aggregator.base_aggregator import BaseAggregator

INDICATOR_INFO = {
    "거래량 절대평균": {
        "label": "거래량 (Absolute Volume)",
        "formula": "mean(volume)",
        "y_format": ",d",
        "y_suffix": "",
    },
    "거래량 정규화평균": {
        "label": "거래량 (Normalized Volume)",
        "formula": "volume / daily_total * 100",
        "y_format": ".4f",
        "y_suffix": "%",
    },
    "시가 절대평균": {
        "label": "시가 (Absolute Open)",
        "formula": "mean(open)",
        "y_format": ",.0f",
        "y_suffix": "",
    },
    "시가 정규화평균": {
        "label": "시가 (Normalized Open)",
        "formula": "(open / first_open - 1) * 100",
        "y_format": ".4f",
        "y_suffix": "%",
    },
    "변동성": {
        "label": "변동성 (Volatility)",
        "formula": "(high - low) / open * 100",
        "y_format": ".4f",
        "y_suffix": "%",
    },
    "방향성": {
        "label": "방향성 (Return)",
        "formula": "(close - open) / open * 100",
        "y_format": ".4f",
        "y_suffix": "%",
    },
    "위치": {
        "label": "위치 (Position)",
        "formula": "(close - low) / (high - low)",
        "y_format": ".4f",
        "y_suffix": "",
    },
}


def get_calc_result(df, indicator):
    calc_map = {
        "거래량 절대평균": calc_volume_abs,
        "거래량 정규화평균": calc_volume_norm,
        "시가 절대평균": calc_open_abs,
        "시가 정규화평균": calc_open_norm,
        "변동성": calc_volatility,
        "방향성": calc_direction,
        "위치": calc_position,
    }
    return calc_map[indicator](df)


def get_combined_results(df):
    return (
        calc_volume_norm(df),
        calc_volatility(df),
        calc_direction(df),
    )


def calc_volume_abs(df):
    return BaseAggregator.calc_absolute_mean(df, "volume")


def calc_volume_norm(df):
    return BaseAggregator.calc_normalized_mean(df, "volume")


def calc_open_abs(df):
    return BaseAggregator.calc_absolute_mean(df, "open")


def calc_open_norm(df):
    df = df.copy()
    first_open = (
        df[df["time"] == "090000"][["ticker", "date", "open"]]
        .rename(columns={"open": "first_open"})
    )
    df = df.merge(first_open, on=["ticker", "date"], how="left")
    df = df.dropna(subset=["first_open"])
    df["val"] = (df["open"] / df["first_open"] - 1) * 100
    return df.groupby("time_label")["val"].mean().reset_index()


def calc_volatility(df):
    df = df.copy()
    df["val"] = (df["high"] - df["low"]) / df["open"] * 100
    df = df.replace([float("inf"), float("-inf")], float("nan")).dropna(subset=["val"])
    return df.groupby("time_label")["val"].mean().reset_index()


def calc_direction(df):
    df = df.copy()
    df["val"] = (df["close"] - df["open"]) / df["open"] * 100
    df = df.replace([float("inf"), float("-inf")], float("nan")).dropna(subset=["val"])
    return df.groupby("time_label")["val"].mean().reset_index()


def calc_position(df):
    df = df.copy()
    df["val"] = (df["close"] - df["low"]) / (df["high"] - df["low"])
    df = df.replace([float("inf"), float("-inf")], float("nan")).dropna(subset=["val"])
    return df.groupby("time_label")["val"].mean().reset_index()

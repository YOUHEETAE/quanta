import plotly.graph_objects as go
from plotly.subplots import make_subplots
from indicators import INDICATOR_INFO

tick_times = [
    f"{h:02d}{m:02d}00"
    for h in range(9, 16)
    for m in range(0, 60, 30)
    if not (h == 15 and m > 30)
]
tick_labels = [f"{t[:2]}:{t[2:4]}" for t in tick_times]

xaxis_config = dict(
    tickvals=tick_labels, ticktext=tick_labels, tickangle=0, tickfont=dict(size=10)
)


def draw_single(result, title, indicator):
    info = INDICATOR_INFO[indicator]
    y_format = info["y_format"]
    y_suffix = info["y_suffix"]
    formula = info["formula"]

    df_normal = result[result["time_label"] < "15:30"]
    df_close = result[result["time_label"] == "15:30"]
    val_range = df_normal["val"].max() - df_normal["val"].min()
    y_min = df_normal["val"].min() - val_range * 0.01
    y_max = df_normal["val"].max() + val_range * 0.01
    hover_format = ",.0f" if y_format == ",d" else ".4f"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_normal["time_label"],
            y=df_normal["val"],
            mode="lines",
            name=info["label"],
            hovertemplate=f"시간: %{{x}}<br>값: %{{y:{hover_format}}}{y_suffix}<br><i>{formula}</i><extra></extra>",
        )
    )
    if not df_close.empty:
        val = df_close["val"].values[0]
        formatted = f"{val:,.0f}" if y_format == ",d" else f"{val:.4f}{y_suffix}"
        fig.add_annotation(
            xref="paper", yref="paper",
            x=1.0, y=1.0,
            xanchor="right", yanchor="top",
            text=f"<b>동시호가 (15:30)</b><br>{formatted}",
            showarrow=False,
            bgcolor="rgba(255, 80, 80, 0.1)",
            bordercolor="rgba(255, 80, 80, 0.6)",
            borderwidth=1,
            borderpad=6,
            font=dict(size=11, color="darkred"),
        )
    fig.update_layout(
        title=title,
        xaxis_title="시간",
        yaxis=dict(tickformat=y_format, ticksuffix=y_suffix, range=[y_min, y_max]),
        xaxis=xaxis_config,
    )
    return fig


def draw_combined(vol_result, vlt_result, ret_result, title):
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        subplot_titles=(
            "거래량 정규화평균 (%)",
            "변동성 / Volatility",
            "방향성 / Return",
        ),
        vertical_spacing=0.08,
    )

    configs = [
        (vol_result, "거래량", "volume / daily_total * 100", "%"),
        (vlt_result, "변동성", "(high - low) / open * 100", "%"),
        (ret_result, "방향성", "(close - open) / open * 100", "%"),
    ]

    for i, (result, name, formula, suffix) in enumerate(configs, 1):
        df_normal = result[result["time_label"] < "15:30"]
        df_close = result[result["time_label"] == "15:30"]

        val_range = df_normal["val"].max() - df_normal["val"].min()
        y_min = df_normal["val"].min() - val_range * 0.01
        y_max = df_normal["val"].max() + val_range * 0.01

        fig.add_trace(
            go.Scatter(
                x=df_normal["time_label"],
                y=df_normal["val"],
                mode="lines",
                name=name,
                hovertemplate=f"시간: %{{x}}<br>값: %{{y:.4f}}{suffix}<br><i>{formula}</i><extra></extra>",
            ),
            row=i,
            col=1,
        )
        if not df_close.empty:
            val = df_close["val"].values[0]
            formatted = f"{val:.4f}{suffix}"
            yref = "y" if i == 1 else f"y{i}"
            fig.add_annotation(
                xref="paper", yref=yref,
                x=1.0, y=y_max,
                xanchor="right", yanchor="top",
                text=f"<b>동시호가 (15:30)</b><br>{formatted}",
                showarrow=False,
                bgcolor="rgba(255, 80, 80, 0.1)",
                bordercolor="rgba(255, 80, 80, 0.6)",
                borderwidth=1,
                borderpad=5,
                font=dict(size=10, color="darkred"),
            )
        fig.update_yaxes(tickformat=".4f", ticksuffix=suffix, range=[y_min, y_max], row=i, col=1)

    fig.update_layout(
        title=title,
        height=700,
        xaxis=xaxis_config,
        xaxis2=xaxis_config,
        xaxis3=dict(**xaxis_config, title="시간"),
    )
    return fig

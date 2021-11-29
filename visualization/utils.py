# Visualization
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pandas import DataFrame
import numpy as np
import matplotlib.pyplot as plt


def plot_heatmap(corr_matrix):
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Heatmap(
            z=corr_matrix.values,
            x=[
                "Open",
                "Close",
                "n_very_bullish",
                "n_very_bearish",
                "n_bullish",
                "n_bearish",
                "n_neutral",
                "change_24hrs",
            ],
            y=[
                "Open",
                "Close",
                "n_very_bullish",
                "n_very_bearish",
                "n_bullish",
                "n_bearish",
                "n_neutral",
                "change_24hrs",
            ],
            type="heatmap",
            colorscale="Viridis",
        ),
        row=1,
        col=1,
    )
    print("Plotting heatmap...")
    fig.show()


def plot_results(dataframe: DataFrame, price_rep="candlestick"):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)
    if price_rep == "bars":
        fig.add_trace(
            go.Bar(
                name="24h Variation",
                x=dataframe.index,
                y=dataframe.change_24hrs,
                offsetgroup=0,
            ),
            row=1,
            col=1,
        )
    elif price_rep == "candlestick":
        fig.add_trace(
            go.Candlestick(
                x=dataframe.index,
                open=dataframe["Open"],
                high=dataframe["High"],
                low=dataframe["Low"],
                close=dataframe["Close"],
                name=f"Price BTC-USDT",
            ),
            row=1,
            col=1,
        )
    fig.add_trace(
        go.Bar(
            name="Very Bullish",
            x=dataframe.index,
            y=dataframe.n_very_bullish,
            offsetgroup=0,
            marker_color="green",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            name="Bullish",
            x=dataframe.index,
            y=dataframe.n_bullish,
            offsetgroup=0,
            marker_color="lightgreen",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            name="Bearish",
            x=dataframe.index,
            y=dataframe.n_bearish,
            offsetgroup=0,
            marker_color="orange",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            name="Very Bearish",
            x=dataframe.index,
            y=dataframe.n_very_bearish,
            offsetgroup=0,
            marker_color="red",
        ),
        row=2,
        col=1,
    )

    fig.update_layout(hovermode="x unified")
    print("Plotting results...")
    fig.show()


def plot_avg_profit_loss(results):
    names = [x["name"] for x in results]
    avg_profits = [x["avg_profit"] for x in results]
    avg_losses = [x["avg_loss"] for x in results]

    N = len(results)
    ind = np.arange(N)
    width = 0.25

    bar6 = plt.bar(ind, avg_profits, width, color="g")
    bar7 = plt.bar(ind + width, avg_losses, width, color="r")

    plt.xlabel("Strategy")
    plt.ylabel("Scores")
    plt.title("Profit v/s Losses")

    plt.xticks(ind + width / 2, names)
    plt.legend((bar6, bar7), ("avg profit", "avg_loss"))
    plt.show()


def plot_win_ratio(results):
    names = [x["name"] for x in results]
    win_ratios = [x["win_ratio"] for x in results]

    N = len(results)
    ind = np.arange(N)
    width = 0.25

    bar1 = plt.bar(ind, win_ratios, width, color="b")

    plt.xlabel("Strategy")
    plt.ylabel("Win ratio")
    plt.title("Win ratios")

    plt.xticks(ind, names)
    plt.show()

    # global_rois = [x["global_roi"] for x in results]
    # profit_factors = [x["profit_factor"] for x in results]
    # avg_hold_times = [x["avg_hold_time"] for x in results]
    # max_drawdowns = [x["max_drawdown"] for x in results]
    # avg_profits = [x["avg_profit"] for x in results]
    # avg_losses = [x["avg_loss"] for x in results]


def plot_balance_history(results):
    return

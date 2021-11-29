import logging
import pandas as pd
from pandas import DataFrame
import numpy as np
import datetime
import matplotlib.pyplot as plt
import pandas_datareader as pdr
import talib

logger = logging.getLogger(__name__)


def macd_rsi_strategy(
    df: DataFrame,
    stake_amount=7000.0,
    starting_balance=10000.0,
    stop_loss=0.05,
    macd_fastperiod=12,
    macd_slowperiod=26,
    macd_signalperiod=9,
    rsi_timeperiod=12,
) -> dict():
    macd, signal, hist = talib.MACD(
        df["Close"],
        fastperiod=macd_fastperiod,
        slowperiod=macd_slowperiod,
        signalperiod=macd_signalperiod,
    )
    df["macd"] = macd
    df["signal"] = signal
    df["hist"] = hist
    df["rsi"] = talib.RSI(df["Close"], timeperiod=rsi_timeperiod)

    trades = list()
    open_trade = False
    current_trade = dict()
    balance = starting_balance
    stake_amount = stake_amount
    prev_row = df.iloc[33]
    for index, row in df.iloc[34:].iterrows():
        if open_trade:
            if (
                row["macd"] < row["signal"]
                # and prev_row["macd"] > prev_row["signal"]
                and row["macd"] > 0
                and row["rsi"] >= 50
            ):
                # close the trade
                current_trade["close_date"] = index
                current_trade["close_rate"] = row["Close"]
                balance += current_trade["amount"] * current_trade["close_rate"]
                current_trade["profit_abs"] = (
                    current_trade["close_rate"] - current_trade["open_rate"]
                ) * current_trade["amount"]
                current_trade["sell_reason"] = "sell_signal"
                current_trade["profit_ratio"] = (
                    current_trade["close_rate"] / current_trade["open_rate"]
                ) - 1
                trades.append(current_trade)
                open_trade = False
                current_trade = dict()
            elif row["Close"] <= current_trade["stop_loss_abs"]:
                # stop loss: close the trade
                current_trade["close_date"] = index
                current_trade["close_rate"] = row["Close"]
                balance += current_trade["amount"] * current_trade["close_rate"]
                current_trade["profit_abs"] = (
                    current_trade["close_rate"] - current_trade["open_rate"]
                ) * current_trade["amount"]
                current_trade["sell_reason"] = "stop_loss"
                current_trade["profit_ratio"] = (
                    current_trade["close_rate"] / current_trade["open_rate"]
                ) - 1
                trades.append(current_trade)
                open_trade = False
                current_trade = dict()
        else:
            if (
                row["macd"] > row["signal"]
                # and prev_row["macd"] < prev_row["signal"]
                and row["macd"] < 0
                and row["rsi"] <= 50
            ):
                # open a trade
                current_trade["open_date"] = index
                current_trade["open_rate"] = row["Close"]
                open_trade = True
                if balance < stake_amount:
                    current_trade["stake_amount"] = balance * 0.7
                else:
                    current_trade["stake_amount"] = stake_amount

                current_trade["stop_loss_ratio"] = stop_loss
                current_trade["stop_loss_abs"] = current_trade["open_rate"] * (
                    1 - stop_loss
                )

                current_trade["amount"] = (
                    current_trade["stake_amount"] / current_trade["open_rate"]
                )
                balance -= current_trade["stake_amount"]
                open_trade = True
        prev_row = row
    if open_trade:
        # logger.info("Unclosed trade detected! Handling...")
        last_trade = trades.pop()
        balance += last_trade["open_rate"] * last_trade["amount"]
    return trades, balance


def bb_rsi_strategy(
    df: DataFrame,
    stake_amount=7000.0,
    starting_balance=10000.0,
    stop_loss=0.05,
    time_period=5,
    nbdevup=2,
    nbdevdn=2,
    matype=0,
    rsi_timeperiod=12,
) -> dict():

    df["upperband"], df["middleband"], df["lowerband"] = talib.BBANDS(
        df["Close"],
        timeperiod=time_period,
        nbdevup=nbdevup,
        nbdevdn=nbdevdn,
        matype=matype,
    )
    df["rsi"] = talib.RSI(df["Close"], timeperiod=rsi_timeperiod)

    trades = list()
    open_trade = False
    current_trade = dict()
    balance = starting_balance
    stake_amount = stake_amount
    for index, row in df.iloc[34:].iterrows():
        if open_trade:
            if row["Close"] >= row["upperband"] and row["rsi"] >= 50:
                # close the trade
                current_trade["close_date"] = index
                current_trade["close_rate"] = row["Close"]
                current_trade["profit_abs"] = (
                    current_trade["close_rate"] - current_trade["open_rate"]
                ) * current_trade["amount"]
                current_trade["sell_reason"] = "sell_signal"
                current_trade["profit_ratio"] = (
                    current_trade["close_rate"] / current_trade["open_rate"]
                ) - 1
                balance += current_trade["amount"] * current_trade["close_rate"]
                trades.append(current_trade)
                open_trade = False
                current_trade = dict()
            elif row["Close"] <= current_trade["stop_loss_abs"]:
                # stop loss: close the trade
                current_trade["close_date"] = index
                current_trade["close_rate"] = row["Close"]
                current_trade["profit_abs"] = (
                    current_trade["close_rate"] - current_trade["open_rate"]
                ) * current_trade["amount"]
                current_trade["sell_reason"] = "stop_loss"
                current_trade["profit_ratio"] = (
                    current_trade["close_rate"] / current_trade["open_rate"]
                ) - 1
                balance += current_trade["amount"] * current_trade["close_rate"]
                trades.append(current_trade)
                open_trade = False
                current_trade = dict()
        else:
            if row["Close"] <= row["middleband"] and row["rsi"] <= 50:
                # open a trade
                current_trade["open_date"] = index
                current_trade["open_rate"] = row["Close"]
                open_trade = True
                if balance < stake_amount:
                    current_trade["stake_amount"] = balance * 0.7
                else:
                    current_trade["stake_amount"] = stake_amount

                current_trade["stop_loss_ratio"] = stop_loss
                current_trade["stop_loss_abs"] = current_trade["open_rate"] * (
                    1 - stop_loss
                )

                current_trade["amount"] = (
                    current_trade["stake_amount"] / current_trade["open_rate"]
                )
                balance -= current_trade["stake_amount"]
                open_trade = True
        prev_row = row
    if open_trade:
        # logger.info("Unclosed trade detected! Handling...")
        last_trade = trades.pop()
        balance += last_trade["open_rate"] * last_trade["amount"]
    return trades, balance

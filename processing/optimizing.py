import logging
import pandas as pd
import plotly.express as px

from strategies.ta_strategies import macd_rsi_strategy, bb_rsi_strategy
from strategies.nlp_strategies import wighted_base_strategy

logger = logging.getLogger(__name__)


def optimize_macd_rsi_strategy(
    df, stake_amount, starting_balance, stop_loss, plot=False
):
    """
    Optimizacion de estrategia MACD + RSI.
    """
    results = dict()
    trades = dict()

    logger.info("Optimizing MACD + RSI strategy...")
    # Probamos distintos valores para los parametros del MACD
    # para buscar la configuracion optima
    for fast_period in [16, 18, 20, 22]:
        for slow_period in [22, 24, 26, 28]:
            for signal_period in [14, 16, 18, 20]:
                for rsi_period in [6, 7, 8, 9]:
                    iteration_trades, balance = macd_rsi_strategy(
                        df,
                        stake_amount=stake_amount,
                        starting_balance=starting_balance,
                        stop_loss=stop_loss,
                        macd_fastperiod=fast_period,
                        macd_slowperiod=slow_period,
                        macd_signalperiod=signal_period,
                        rsi_timeperiod=rsi_period,
                    )
            key = f"{fast_period}_{slow_period}_{signal_period}_{rsi_period}"
            results[key] = balance
            trades[key] = iteration_trades

    df = pd.DataFrame({"config": results.keys(), "balance": results.values()})
    max_value = 0
    max_key = ""

    for index, row in df.iterrows():
        if row["balance"] > max_value:
            max_value = row["balance"]
            max_key = row["config"]

    if plot:
        fig = px.histogram(df, x="config", y="balance")
        fig.show()

    (
        optimal_fastperiod,
        optimal_slowperiod,
        optimal_signalperiod,
        optimal_rsiperiod,
    ) = max_key.split("_")
    return (
        int(optimal_fastperiod),
        int(optimal_slowperiod),
        int(optimal_signalperiod),
        int(optimal_rsiperiod),
        trades[max_key],
        results[max_key],
    )


def optimize_bb_rsi_strategy(df, stake_amount, starting_balance, stop_loss, plot=False):
    """
    Optimizacion de estrategia BB + RSI.
    """
    results = dict()
    trades = dict()

    logger.info("Optimizing BB + RSI strategy...")
    # Probamos distintos valores para los parametros del MACD
    # para buscar la configuracion optima
    for time_period in [20, 22, 24, 26]:
        for std_up in [2, 3, 4, 5]:
            for std_down in [2, 3, 4, 5]:
                for rsi_period in [6, 7, 8, 9]:
                    iteration_trades, balance = bb_rsi_strategy(
                        df,
                        stake_amount=stake_amount,
                        starting_balance=starting_balance,
                        stop_loss=stop_loss,
                        time_period=time_period,
                        nbdevup=std_up,
                        nbdevdn=std_down,
                        matype=0,
                        rsi_timeperiod=rsi_period,
                    )
            key = f"{time_period}_{std_up}_{std_down}_{rsi_period}"
            results[key] = balance
            trades[key] = iteration_trades

    df = pd.DataFrame({"config": results.keys(), "balance": results.values()})
    max_value = 0
    max_key = ""

    for index, row in df.iterrows():
        if row["balance"] > max_value:
            max_value = row["balance"]
            max_key = row["config"]

    if plot:
        fig = px.histogram(df, x="config", y="balance")
        fig.show()

    (
        optimal_time_period,
        optimal_std_up,
        optimal_std_down,
        optimal_rsiperiod,
    ) = max_key.split("_")
    return (
        int(optimal_time_period),
        int(optimal_std_up),
        int(optimal_std_down),
        int(optimal_rsiperiod),
        trades[max_key],
        results[max_key],
    )


def optimize_nlp_weighted_strategy(
    df, stake_amount, starting_balance, stop_loss, plot=False
):
    """
    Optimizacion de estrategia NLP con pesos.
    """
    results = dict()
    trades = dict()
    logger.info("Optimizing NLP weighted strategy....")

    # Probamos distintos valores para los pesos de las noticias muy positivas/negativas
    # para buscar la configuracion optima
    for weight in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        iteration_trade, balance = wighted_base_strategy(
            df,
            stake_amount=stake_amount,
            starting_balance=starting_balance,
            stop_loss=stop_loss,
            weight=weight,
        )
        key = f"{weight}"
        results[key] = balance
        trades[key] = iteration_trade

    df = pd.DataFrame({"config": results.keys(), "balance": results.values()})
    max_value = 0
    max_key = ""

    for index, row in df.iterrows():
        if row["balance"] > max_value:
            max_value = row["balance"]
            max_key = row["config"]

    if plot:
        fig = px.histogram(df, x="config", y="balance")
        fig.show()

    return float(max_key), trades[max_key], results[max_key]

import logging
import pandas as pd
import plotly.express as px

from strategies.ta_strategies import macd_rsi_strategy

logger = logging.getLogger(__name__)


def optimize_macd_rsi_strategy(
    df, stake_amount, starting_balance, stop_loss, plot=False
):
    """
    Optimizacion de estrategia MACD + RSI.
    """
    results = dict()
    logger.info("Optimizing MACD + RSI strategy...")

    # Probamos distintos valores para los parametros del MACD
    # para buscar la configuracion optima
    for fast_period in [16, 18, 20, 22]:
        for slow_period in [22, 24, 26, 28]:
            for signal_period in [14, 16, 18, 20]:
                _, balance = macd_rsi_strategy(
                    df,
                    stake_amount=stake_amount,
                    starting_balance=starting_balance,
                    stop_loss=stop_loss,
                    macd_fastperiod=fast_period,
                    macd_slowperiod=slow_period,
                    macd_signalperiod=signal_period,
                    rsi_timeperiod=12,
                )
            key = f"{fast_period}_{slow_period}_{signal_period}"
            results[key] = balance

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

    optimal_fastperiod, optimal_slowperiod, optimal_signalperiod = max_key.split("_")
    return int(optimal_fastperiod), int(optimal_slowperiod), int(optimal_signalperiod)

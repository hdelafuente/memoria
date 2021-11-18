import warnings
import pprint

warnings.filterwarnings("ignore")
import logging

# Procesamiento
from processing.backtest import get_backtest_results, print_results
from data import load_and_estimate, build_dataframe
from processing.optimizing import (
    optimize_macd_rsi_strategy,
    optimize_nlp_weighted_strategy,
)

# Visualizacion
from visualization.utils import *

# Configuracion
from decouple import config

logging.basicConfig(
    format="[%(asctime)s] %(filename)s %(levelname)s: %(message)s", level=logging.INFO
)
logger = logging.getLogger("memoria")

PLOT_NEWS = config("PLOT_NEWS", default=False, cast=bool)
PLOT_BACKTEST = config("PLOT_BACKTEST", default=False, cast=bool)
TICKER = config("TICKER", default="BTC-USD", cast=str)


if __name__ == "__main__":
    test = load_and_estimate("test.csv")
    btc, matrix = build_dataframe(test, TICKER)

    starting_balance = config("INIT_BALANCE", default=1000.0, cast=float)
    stake_amount = config("STAKE_AMOUNT", default=1000.0, cast=float)
    stop_loss = config("STOP_LOSS", default=0.05, cast=float)

    logger.info("Backtest configurations")
    logger.info(f"Starting balance: $ {starting_balance:3.2f}")
    logger.info(f"Stake amount: $ {stake_amount:3.2f}")
    logger.info(f"Stop loss: {stop_loss*100:3.2f} %")
    logger.info("Starting backtests...")

    optimal_weight, nlp_weight_trades, nlp_balance = optimize_nlp_weighted_strategy(
        btc, stake_amount, starting_balance, stop_loss, plot=False
    )

    _, _, _, _, macd_trades, macd_balance = optimize_macd_rsi_strategy(
        btc, stake_amount, starting_balance, stop_loss, plot=False
    )
    # TODO: implementar en processing.backtest salida de los trades
    # TODO: implementar output de los trades: max profit, min profit, wins/loses/draws, avg profit, avg loss
    # TODO: implementar opcion de mostrar rangos de fechas
    # TODO: integrar de comparacion y rango de fechas

    macd_results = get_backtest_results(
        macd_trades, macd_balance, name="MACD + RSI", starting_balance=starting_balance
    )

    nlp_results = get_backtest_results(
        nlp_weight_trades,
        nlp_balance,
        name="NLP with Weights",
        starting_balance=starting_balance,
    )
    
    results = [macd_results, nlp_results]

    plot_avg_profit_loss(results)
    plot_win_ratio(results)
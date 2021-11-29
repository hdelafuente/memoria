import warnings
import pprint

warnings.filterwarnings("ignore")
import logging

# Procesamiento
from strategies.nlp_strategies import wighted_base_strategy
from processing.backtest import get_backtest_results
from data import load_and_estimate, build_dataframe
from processing.optimizing import (
    optimize_macd_rsi_strategy,
    optimize_nlp_weighted_strategy,
    optimize_bb_rsi_strategy,
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

    base_nlp_trades, base_nlp_balance = wighted_base_strategy(
        btc,
        stake_amount=stake_amount,
        starting_balance=starting_balance,
        stop_loss=stop_loss,
        weight=1.0,
    )

    _, _, _, _, macd_trades, macd_balance = optimize_macd_rsi_strategy(
        btc, stake_amount, starting_balance, stop_loss, plot=False
    )
    _, _, _, _, bb_trades, bb_balance = optimize_bb_rsi_strategy(
        btc, stake_amount, starting_balance, stop_loss, plot=False
    )

    # TODO: implementar opcion de mostrar rangos de fechas
    # TODO: integrar de comparacion y rango de fechas

    bb_results = get_backtest_results(
        bb_trades, bb_balance, name="BB + RSI", starting_balance=starting_balance
    )

    macd_results = get_backtest_results(
        macd_trades, macd_balance, name="MACD + RSI", starting_balance=starting_balance
    )

    base_nlp_results = get_backtest_results(
        base_nlp_trades,
        base_nlp_balance,
        name="NLP without Weights",
        starting_balance=starting_balance,
    )

    nlp_results = get_backtest_results(
        nlp_weight_trades,
        nlp_balance,
        name="NLP with Weights",
        starting_balance=starting_balance,
    )

    results = [base_nlp_results, nlp_results, macd_results, bb_results]

    for i in results:
        print("=====================================")
        print(i["name"])
        print(f"Max profit: {i['max_profit']:3.2f}%")
        print(f"Min profit: {i['min_profit']:3.2f}%")
        print(f"Wins: {i['wins']}")
        print(f"Loses: {i['losses']}")
        print(f"Avg. profit: {i['avg_profit']}")
        print(f"Avg. loss: {i['avg_loss']}")
        print(f"ROI: {i['global_roi']}")
        print(f"max_drawdown: {i['max_drawdown']}")
        print(f"starting_balance: ${i['starting_balance']}")
        print(f"final_balance:    ${i['final_balance']}")
        print(f"avg_hold_time: {i['avg_hold_time']:3.2f} days")
    # plot_avg_profit_loss(results)
    # plot_win_ratio(results)

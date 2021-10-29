import warnings

warnings.filterwarnings("ignore")
import logging

# Processing
from pandas import DataFrame
from strategies.nlp_strategies import base_strategy, wighted_base_strategy
from strategies.ta_strategies import macd_rsi_strategy
from processing.backtest import get_backtest_results
from processing.data import load_and_estimate, build_dataframe

# Visualization
from visualization.utils import plot_results
import pprint as pp

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
    logger.info(f"Stop loss: {stop_loss} %")
    logger.info("Starting backtests...")

    base_strategy_trades, balance = base_strategy(
        btc,
        stake_amount=stake_amount,
        starting_balance=starting_balance,
        stop_loss=stop_loss,
    )
    base_weighted_strategy_trades, balance2 = wighted_base_strategy(
        btc,
        stake_amount=stake_amount,
        starting_balance=starting_balance,
        stop_loss=stop_loss,
    )
    macd_trades, balance3 = macd_rsi_strategy(
        btc,
        stake_amount=stake_amount,
        starting_balance=starting_balance,
        stop_loss=stop_loss,
    )

    print("==============================")
    print("Base strategy result")
    print(f"Final balance: $ {balance:3.2f}")
    print(f"Total Profit: {(balance * 100 /starting_balance):3.2f} %")

    print("==============================")
    print("Base weighted strategy result")
    print(f"Final balance: $ {balance2:3.2f}")
    print(f"Total Profit: {(balance2 * 100 / starting_balance):3.2f} %")

    print("==============================")
    print("MACD + RSI strategy result")
    print(f"Final balance: $ {balance3:3.2f}")
    print(f"Total Profit: {(balance3 * 100 / starting_balance):3.2f} %")
    print("==============================")
    if PLOT_NEWS:
        plot_results(btc)

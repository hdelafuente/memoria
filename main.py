import warnings

warnings.filterwarnings("ignore")
# Processing
from pandas import DataFrame

from strategies.nlp_strategies import base_strategy
from processing.backtest import get_backtest_results
from processing.data import load_and_estimate, build_dataframe

# Visualization
from visualization.utils import plot_results
import pprint as pp

# Configuracion
from decouple import config


PLOT_NEWS = config("PLOT_NEWS", default=False, cast=bool)
PLOT_BACKTEST = config("PLOT_BACKTEST", default=False, cast=bool)
TICKER = config("TICKER", default="BTC-USD", cast=str)



if __name__ == "__main__":
    test = load_and_estimate("test.csv")
    btc, matrix = build_dataframe(test, TICKER)

    starting_balance = config("INIT_BALANCE", default=1000.0, cast=float)
    stake_amount = config("STAKE_AMOUNT", default=1000.0, cast=float)
    stop_loss = config("STOP_LOSS", default=0.05, cast=float)

    print("Backtest configurations")
    print(f"Starting balance: {starting_balance}")
    print(f"Stake amount: {stake_amount}")
    print(f"Stop loss: {stop_loss}")

    base_strategy_trades, balance = base_strategy(btc, stake_amount=stake_amount, starting_balance=starting_balance, stop_loss=stop_loss)
    #get_backtest_results(base_strategy_trades, name="Base Strategy")
    print(f"Final balance: $ {balance:3.2f}")
    print(f"Total Profit: $ {(balance-starting_balance):3.2f}")

    if PLOT_NEWS:
        plot_results(btc)

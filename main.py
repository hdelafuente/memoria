import warnings

warnings.filterwarnings("ignore")
# Processing
from pandas import DataFrame

from strategies.nlp_strategies import base_strategy
from processing.backtest import get_backtest_results
from processing.data import load_and_estimate, build_dataframe

# Visualization
from visualization.utils import plot_results

# Configuracion
from decouple import config


PLOT_NEWS = config("PLOT_NEWS", default=False)
PLOT_BACKTEST = config("PLOT_BACKTEST", default=False)
TICKER = config("TICKER", default="BTC-USD")



if __name__ == "__main__":
    test = load_and_estimate("test.csv")
    btc, matrix = build_dataframe(test, TICKER)

    starting_balance = config("INIT_BALANCE")
    stake_amount = config("STAKE_AMOUNT")

    base_strategy_trades = base_strategy(btc, stake_amount=stake_amount, starting_balance=starting_balance)
    get_backtest_results(base_strategy_trades, name="Base Strategy")

    if PLOT_NEWS:
        plot_results(btc)

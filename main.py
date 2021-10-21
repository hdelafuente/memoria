import warnings

warnings.filterwarnings("ignore")
# Processing
from pandas import DataFrame

from strategies.nlp_strategies import base_strategy
from processing.backtest import get_backtest_results
from processing.data import load_and_estimate, build_dataframe

# Visualization
from visualization.utils import plot_results

# Configurations
# TODO: decouple
WRITE_CSV = False
PLOT_NEWS = False
PLOT_BACKTEST = True
TICKER = "BTC-USD"


def export_csv(file_name: str, dataframe: DataFrame):
    # Write the dataframe into a csv file
    print(f"Exporting results into: {file_name}")
    output_file = open(file_name, "w")
    dataframe.to_csv(path_or_buf=output_file, index=True, sep="|")
    output_file.close()
    print("Successful export!")


if __name__ == "__main__":
    test = load_and_estimate("test.csv")
    btc, matrix = build_dataframe(test, TICKER)

    base_strategy_trades = base_strategy(btc)
    get_backtest_results(base_strategy_trades, name="Base Strategy")

    if WRITE_CSV:
        export_csv("BTC-USD-polarity.csv", btc)

    if PLOT_NEWS:
        plot_results(btc)

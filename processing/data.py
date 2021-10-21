import warnings

warnings.filterwarnings("ignore")
from pathlib import Path
import os
from tqdm import tqdm
import pandas as pd
from textblob import TextBlob
import pandas_datareader as pdr

data_path = Path("data")
if not data_path.exists():
    data_path.mkdir(parents=True)


def estimate_polarity(text: str):
    return TextBlob(text).sentiment.polarity


def load_and_estimate(file_name: str) -> pd.DataFrame:
    test = pd.read_csv(
        os.path.join(data_path, file_name),
        sep="|",
        parse_dates=["date"],
        date_parser=lambda col: pd.to_datetime(col, utc=True),
        infer_datetime_format=True,
    )
    test = test.sort_values(by="date")
    test.set_index("date")
    test["polarity"] = test.text.apply(estimate_polarity)
    return test


def group_news(test: pd.DataFrame) -> dict:
    print("Grouping news by polarity...")
    temp = dict()
    indexes = test.index
    for row in tqdm(test.values):
        row_date = row[1].date().strftime("%Y-%m-%d")
        if row_date not in temp:
            # 0: positives, 1: neutral-postive, 2: neutral, 3: neutral-negative, 4: negatives,
            temp[row_date] = [0, 0, 0, 0, 0]
        polarity = row[2]
        if polarity == 0.0:  # neutral
            temp[row_date][2] += 1
        elif polarity > 0.0 and polarity < 0.5:  # neutral-positive
            temp[row_date][1] += 1
        elif polarity > 0.0 and polarity >= 0.5:  # postive
            temp[row_date][0] += 1
        elif polarity < 0.0 and polarity > -0.5:  # neutral-negative
            temp[row_date][3] += 1
        elif polarity < 0.0 and polarity <= -0.5:  # negative
            temp[row_date][4] += 1
    return temp


def build_dataframe(test: pd.DataFrame, ticker: str) -> pd.DataFrame:
    # Ticker price hisotry extraction
    start_date = test.iloc[0].date
    end_date = test.iloc[-1].date
    print(f"Starting Date: {start_date} \nEnding Date: {end_date}")
    df = pdr.DataReader(ticker, "yahoo", start_date, end_date)
    results = group_news(test)
    print(f"Generating dataframe for: {ticker}")
    print("Mapping grouped news by date...")
    df["n_very_bullish"] = df.apply(
        lambda x: results[x.name.date().strftime("%Y-%m-%d")][0]
        if x.name.date().strftime("%Y-%m-%d") in results.keys()
        else 0,
        axis=1,
    )
    df["n_very_bearish"] = df.apply(
        lambda x: results[x.name.date().strftime("%Y-%m-%d")][4]
        if x.name.date().strftime("%Y-%m-%d") in results.keys()
        else 0,
        axis=1,
    )
    df["n_bullish"] = df.apply(
        lambda x: results[x.name.date().strftime("%Y-%m-%d")][1]
        if x.name.date().strftime("%Y-%m-%d") in results.keys()
        else 0,
        axis=1,
    )
    df["n_bearish"] = df.apply(
        lambda x: results[x.name.date().strftime("%Y-%m-%d")][3]
        if x.name.date().strftime("%Y-%m-%d") in results.keys()
        else 0,
        axis=1,
    )
    df["n_neutral"] = df.apply(
        lambda x: results[x.name.date().strftime("%Y-%m-%d")][2]
        if x.name.date().strftime("%Y-%m-%d") in results.keys()
        else 0,
        axis=1,
    )
    df["change_24hrs"] = df.apply(
        lambda x: (x["Close"] * 100.0 / x["Open"] - 100.0), axis=1
    )
    # Cut the dataframe to get the past year only
    print("Filtering dates...")
    return_start_date = "2020-12-31"
    after_start_date = df.index >= return_start_date
    filtered_dates = df.loc[after_start_date]
    print("Dataframe generated!")
    corr_matrix = df.corr("pearson")
    return filtered_dates, corr_matrix
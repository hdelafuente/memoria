from pandas import DataFrame

# Base strategy
def base_strategy(df: DataFrame, stake_amount=1000, starting_balance=1000) -> dict:
    # En orden las columnas:
    # High, Low, Open, Close, Volume, Adj Close, very_bullish,
    # very_bearish, bullish, bearish, neutral, change_24hrs
    btc_amount = 0
    balance = starting_balance
    trades = list()
    open_trade = False
    print("Starting backtest...")
    current_trade = dict()
    trade_id = 0
    indexes = df.index
    for date, row in zip(indexes, df.values):
        (
            high,
            low,
            open_price,
            close_price,
            volume,
            adj_close,
            n_very_bullish,
            n_very_bearish,
            n_bullish,
            n_bearish,
            n_neutral,
            change_24hrs,
        ) = row
        if n_bullish > n_bearish and not open_trade:
            # buy signal...
            current_trade["id"] = trade_id
            open_trade = True
            if balance < stake_amount:
                btc_amount = balance / close_price
            else:
                btc_amount = stake_amount / close_price

            current_trade["open_price"] = close_price
            current_trade["open_date"] = date
            current_trade["coin_amount"] = btc_amount

        elif n_bearish > n_bullish and open_trade:
            # sell signal...
            open_trade = False
            balance = close_price * btc_amount
            current_trade["close_price"] = close_price
            current_trade["close_date"] = date
            current_trade["after_balance"] = balance
            btc_amount = 0
            trades.append(current_trade)
            trade_id += 1
            current_trade = dict()
        elif n_neutral > n_bearish and n_neutral > n_bullish:
            # hold...
            continue
    return trades

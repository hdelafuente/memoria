import logging
from pandas import DataFrame

logger = logging.getLogger(__name__)


def register_open_trade(
    trade_id: int, balance: float, stake_amount: float, open_rate: float, date
) -> dict:
    trade = dict()
    trade["id"] = trade_id

    amount = 0

    # Vemos si usamos el total del balance o
    # el stake_amount
    if balance < stake_amount:
        amount = balance*0.7 / open_rate
        trade["stake_amount"] = balance
    else:
        trade["stake_amount"] = stake_amount
        amount = stake_amount / open_rate

    # Guardamos info del trade y descontamos del balance
    trade["open_rate"] = open_rate
    trade["open_date"] = date
    trade["amount"] = amount
    return trade


def register_close_trade(
    trade: dict, open_rate: float, close_rate: float, amount: float, date, reason
):
    trade["close_rate"] = close_rate
    trade["close_date"] = date
    trade["sell_reason"] = reason
    trade["profit_abs"] = close_rate * amount - open_rate * amount
    trade["profit_ratio"] = (close_rate / open_rate) - 1
    return 0


# Base strategy
def wighted_base_strategy(
    df: DataFrame,
    stake_amount=1000.0,
    starting_balance=1000.0,
    stop_loss=0.05,
    weight=1.0,
) -> dict:
    """
    En orden las columnas del dataframe:
      High, Low, Open, Close, Volume, Adj Close, very_bullish,
      very_bearish, bullish, bearish, neutral, change_24hrs

    Consideraciones:
      * La estrategia compra al final del dia
      * Noticias muy positivas y muy negativas tienen un peso de 1.5


    starting_balance: int > 0
    stake_amount: int > 0
    stop_loss: float [0,1]
    """
    btc_amount = 0
    balance = starting_balance
    trades = list()
    open_trade = False
    current_trade = dict()
    current_trade["stop_loss_abs"] = 0
    trade_id = 0
    for date, row in df.iterrows():
        close_price = row["Close"]
        n_very_bullish = row["n_very_bullish"]
        n_very_bearish = row["n_very_bearish"]
        n_bullish = row["n_bullish"]
        n_bearish = row["n_bearish"]
        n_neutral = row["n_neutral"]

        if open_trade:
            # Con un trade abierto verificamos si hay señal de venta
            if (
                weight * n_very_bullish + n_bullish
                < weight * n_very_bearish + n_bearish
            ):
                # sell signal...
                open_trade = False

                # Guardamos info del trade y agregamos al balance
                balance += close_price * current_trade["amount"]
                register_close_trade(
                    current_trade,
                    current_trade["open_rate"],
                    close_price,
                    btc_amount,
                    date,
                    "sell_signal",
                )
                btc_amount = 0
                trades.append(current_trade)

                trade_id += 1
                current_trade = dict()
                current_trade["stop_loss_abs"] = 0
            elif close_price <= current_trade["stop_loss_abs"]:
                # sell signal por stop_loss
                open_trade = False
                # Guardamos info del trade y agregamos al balance
                balance += close_price * current_trade["amount"]
                register_close_trade(
                    current_trade,
                    current_trade["open_rate"],
                    close_price,
                    btc_amount,
                    date,
                    "stop_loss",
                )
                btc_amount = 0
                trades.append(current_trade)

                trade_id += 1
                current_trade = dict()
                current_trade["stop_loss_abs"] = 0
        else:
            # Verificamos si hay señal de compra
            if (
                weight * n_very_bullish + n_bullish
                > weight * n_very_bearish + n_bearish
                and balance > 0
            ):
                # buy signal...
                open_trade = True
                current_trade = register_open_trade(
                    trade_id, balance, stake_amount, close_price, date
                )

                # Descontamos del balance lo que se uso para el trade
                balance -= current_trade["stake_amount"]
                btc_amount = current_trade["amount"]
                # Fijamos el precio de stop loss
                if stop_loss > 0.0:
                    current_trade["stop_loss_ratio"] = stop_loss
                    current_trade["stop_loss_abs"] = close_price * (1 - stop_loss)

    if open_trade:
        # logger.info("Unclosed trade detected! Handling...")
        last_trade = trades.pop()
        balance += last_trade["open_rate"] * last_trade["amount"]
    return trades, balance

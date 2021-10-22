from pandas import DataFrame

def register_open_trade(trade_id: int, balance: float, stake_amount: float, open_rate: float, date) -> dict:
  trade = dict()
  trade["id"] = trade_id

  amount = 0
            
  # Vemos si usamos el total del balance o 
  # el stake_amount
  if balance < stake_amount:
      amount = balance / open_rate
  else:
      amount = stake_amount / open_rate

  
  
  # Guardamos info del trade y descontamos del balance
  trade["open_rate"] = open_rate
  trade["open_date"] = date
  trade["amount"] = amount
  return trade

def register_close_trade(trade: dict, open_rate: float, close_rate: float, amount: float, date, reason):
  trade["close_rate"] = close_rate
  trade["close_date"] = date
  trade["sell_reason"] = reason
  trade["profit_abs"] = (close_rate - open_rate) * amount
  trade["profit_ratio"] = (close_rate / open_rate) - 1
  return 0

# Base strategy
def base_strategy(df: DataFrame, stake_amount=1000.0, starting_balance=1000.0, stop_loss=0.05) -> dict:
    """
    En orden las columnas:
      High, Low, Open, Close, Volume, Adj Close, very_bullish,
      very_bearish, bullish, bearish, neutral, change_24hrs
    
    Consideraciones:
      * La estrategia compra al final del dia
      * Noticias positivas y negativas pesan lo mismo

    starting_balance: int > 0
    stake_amount: int > 0
    stop_loss: float [0,1]
    """
    btc_amount = 0
    balance = starting_balance
    trades = list()
    open_trade = False
    print("Starting backtest...")
    current_trade = dict()
    current_trade["stop_loss_abs"] = 0
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
        if not open_trade:
          # Verificamos si hay señal de compra
          if n_bullish > n_bearish and balance > 0:
            # buy signal...
            open_trade = True 
            current_trade = register_open_trade(trade_id, balance, stake_amount, close_price, date)
            amount = 0
            
            # Vemos si usamos el total del balance o 
            # el stake_amount
            if balance < stake_amount:
                balance -= balance
            else:
                balance -= stake_amount
            btc_amount = current_trade["amount"]
            # Fijamos el precio de stop loss
            if stop_loss > 0.0:
              current_trade["stop_loss_ratio"] = stop_loss
              current_trade["stop_loss_abs"] = close_price * (1 - stop_loss)

        else:
          # Con un trade abierto verificamos si hay señal de venta
          if n_bearish > n_bullish:
              # sell signal...
              open_trade = False
              
              # Guardamos info del trade y agregamos al balance
              balance += close_price * current_trade["amount"]
              register_close_trade(current_trade, current_trade["open_rate"], close_price, btc_amount, date, "sell_signal")   
              btc_amount = 0
              trades.append(current_trade)

              trade_id += 1
              current_trade = dict()
              current_trade["stop_loss_abs"] = 0
          elif close_price < current_trade["stop_loss_abs"]:
              # sell signal por stop_loss
              open_trade = False
              # Guardamos info del trade y agregamos al balance
              balance += close_price * current_trade["amount"]
              register_close_trade(current_trade, current_trade["open_rate"], close_price, btc_amount, date, "stop_loss")
              btc_amount = 0
              trades.append(current_trade)

              trade_id += 1
              current_trade = dict()
              current_trade["stop_loss_abs"] = 0
          else:
            # HODL...
            continue
    if open_trade:
      print("[INFO] Unclosed trade detected!")
      print("Handling trade and balance...")
      last_trade = trades.pop()
      balance += last_trade["open_rate"] * last_trade["amount"]
    return trades, balance

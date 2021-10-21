from tqdm import tqdm
import pprint as pp


def get_backtest_results(trades: dict, name="", starting_balance=1000):
    """
    trades: dict
    {
      'id',
      'open_price',
      'open_date',
      'coin_amount',
      'close_price',
      'close_date',
      'after_balance'

    }
    """
    avg_profit = 0
    max_profit = 0
    min_profit = 0
    max_balance = 0
    min_balance = 0
    wins = 0
    losses = 0
    prev_balance = 0
    print("Processing backtest results...")
    final_balance = trades[-1]["after_balance"]
    total_profit = final_balance - starting_balance
    for trade in tqdm(trades):
        if prev_balance == 0:
            profit = (trade["after_balance"] - starting_balance) / starting_balance
        else:
            profit = (trade["after_balance"] - prev_balance) / prev_balance

        avg_profit += profit
        if profit > 0:
            wins += 1
            if profit >= max_profit:
                max_profit = profit * 100.0
        elif profit < 0:
            losses += 1
            if profit <= min_profit:
                min_profit = profit * 100.0

        prev_balance = trade["after_balance"]
        if min_balance == 0:
            min_balance = prev_balance

        if prev_balance > max_balance:
            max_balance = prev_balance
        elif prev_balance < min_balance:
            min_balance = prev_balance

    avg_profit /= len(trades)
    print(f"----------- {name} backtest results -----------")
    print(f"starting balance: $ {starting_balance:3.2f}")
    print(f"final balance: $ {final_balance:3.2f}")
    print(f"max balance: $ {max_balance:3.2f}")
    print(f"min balance: $ {min_balance:3.2f}")
    print(f"total profit: $ {total_profit:3.2f}")
    print(f"wins/losses: {wins}/{losses}")
    print(f"avg profit: {avg_profit:3.5} %")
    print(f"max profit: {max_profit:3.2f} %")
    print(f"min profit: {min_profit:3.2f} %")
    return True

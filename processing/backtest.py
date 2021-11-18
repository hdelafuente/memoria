import logging
import pprint as pp

logger = logging.getLogger(__name__)


def get_backtest_results(trades: dict, final_balance, name="", starting_balance=1000):
    """
    Calculates max profit, min profit, avg profit, avg loss, wins/loses/draws,
    """
    avg_profit = 0
    avg_loss = 0
    max_profit = 0
    min_profit = 0
    wins = 0
    losses = 0

    avg_hold_time = 0

    profit_factor_wins = 0
    profit_factor_losses = 0

    max_balance = 0
    min_balance = 0

    balance = starting_balance

    balance_history = dict()

    roi_history = dict()

    sell_reasons = {"stop_loss": 0, "sell_signal": 0}
    logger.info(f"Processing {name} backtest results...")
    for trade in trades:
        # para verificar el balance
        balance_history[trade["open_date"]] = balance
        balance -= trade["stake_amount"]
        balance += trade["amount"] * trade["close_rate"]
        balance_history[trade["close_date"]] = balance

        roi0 = (
            (trade["close_rate"] * trade["amount"]) - trade["stake_amount"]
        ) / trade["stake_amount"]
        roi_history[trade["close_date"]] = roi0

        if balance > max_balance:
            max_balance = balance

        if balance < min_balance or min_balance == 0:
            min_balance = balance

        sell_reasons[trade["sell_reason"]] += 1
        profit = trade["profit_ratio"] * 100.0

        avg_hold_time += (trade["close_date"] - trade["open_date"]).days

        if profit > 0:
            avg_profit += profit
            wins += 1
            profit_factor_wins += trade["profit_abs"]
            if profit >= max_profit:
                max_profit = profit
        elif profit < 0:
            avg_loss += profit
            losses += 1
            profit_factor_losses += -1 * trade["profit_abs"]
            if profit <= min_profit:
                min_profit = profit

    # avg profit
    if wins > 0:
        avg_profit /= wins
    else:
        avg_profit = 0
    # avg loss
    if losses > 0:
        avg_loss /= losses
    else:
        avg_loss = 0

    # abs profit y roi
    abs_profit = final_balance - starting_balance
    roi = abs_profit / starting_balance * 100.0

    avg_hold_time = avg_hold_time / len(trades)

    # profit factor nos ayuda a medir cuanta plata se gano sobre la que se perdio
    # una valor entre el 1.4 y 2.0 es bueno para un estrategia
    if profit_factor_losses > 0:
        profit_factor = profit_factor_wins / profit_factor_losses
    else:
        profit_factor = "inf"

    # win ratio
    win_ratio = wins / (wins + losses) * 100.0

    # max drawdown
    max_drawdown = (max_balance - min_balance) / max_balance

    return {
        "name": name,
        "starting_balance": starting_balance,
        "final_balance": final_balance,
        "avg_profit": avg_profit,
        "avg_loss": avg_loss,
        "max_profit": max_profit,
        "min_profit": min_profit,
        "wins": wins,
        "losses": losses,
        "win_ratio": win_ratio,
        "sell_reasons": sell_reasons,
        "abs_profit": abs_profit,
        "global_roi": roi,
        "roi_history": roi_history,
        "profit_factor": profit_factor,
        "avg_hold_time": avg_hold_time,
        "max_drawdown": max_drawdown,
        "max_balance": max_balance,
        "min_balance": min_balance,
        "balance_history": balance_history,
    }


def print_results(
    name,
    starting_balance,
    final_balance,
    avg_profit,
    max_profit,
    min_profit,
    wins,
    losses,
    sell_reasons,
    abs_profit,
    abs_percent_profit,
):
    """
    Prints backtest results
    """
    print(f"----------- {name} backtest results -----------")
    print(f"starting balance: $ {starting_balance:3.2f}")
    print(f"final balance:    $ {final_balance:3.2f}")
    print(f"abs profit ($):  $ {abs_profit:3.2f}")
    print(f"abs profit (%):    {abs_percent_profit:3.2f}%")
    print(f"wins/losses:        {wins}/{losses}")
    print(f"avg profit: {avg_profit:3.2f}%")
    print(f"max profit: {max_profit:3.2f}%")
    print(f"min profit: {min_profit:3.2f}%")
    return 0

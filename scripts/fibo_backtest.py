# from backtesting import Backtest
# from fibo_algo import FibonacciStrategy
# from backtesting.test import GOOG  # Use historical Google stock data as an example
# import pandas_ta as ta

# def backtest_fibonacci_strategy(initial_balance=10000):
#     """
#     Backtest the Fibonacci strategy using historical Google stock data.
    
#     Parameters:
#         initial_balance (float): Starting balance for the backtest.
    
#     Returns:
#         Backtest: Backtest object with results.
#     """
#     # Use historical Google stock data as an example
#     df = GOOG.copy()
#     df["RSI"] = ta.rsi(df["Close"], length=12)
#     df["EMA"] = ta.ema(df["Close"], length=150)

#     bt = Backtest(df, FibonacciStrategy, cash=initial_balance, commission=.002)
#     stats = bt.run()
#     bt.plot()
#     return stats

# # Example usage
# stats = backtest_fibonacci_strategy(initial_balance=10000)
# print(stats)

from backtesting import Backtest
from fibo_algo import FibonacciStrategy
from backtesting.test import GOOG  # Example dataset

# Run the backtest
bt = Backtest(GOOG, FibonacciStrategy, cash=10000, commission=.002)
stats = bt.run()
bt.plot()

print(stats)

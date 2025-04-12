from backtesting import Backtest, Strategy
import pandas_ta as ta
import pandas as pd

# Ensure pandas_ta is properly initialized
pd.options.mode.chained_assignment = None  # Suppress warnings
ta.strategy = None  # Reset any existing strategy

class FibonacciStrategy(Strategy):
    """
    A strategy class for the backtesting package.
    """
    def init(self):
        # Convert _Array to Pandas Series for compatibility with pandas_ta
        close_series = pd.Series(self.data.Close, index=self.data.index)
        self.rsi = ta.rsi(close_series, length=12)  # Use pandas_ta directly
        self.ema = ta.ema(close_series, length=150)

    def next(self):
        # Skip if not enough data
        if len(self.data) < 150:
            return

        # Trend detection
        ema_signal = 0
        if self.data.Close[-1] > self.ema[-1]:
            ema_signal = 2  # Uptrend
        elif self.data.Close[-1] < self.ema[-1]:
            ema_signal = 1  # Downtrend

        # Impulse detection
        if ema_signal == 2 and self.data.High[-1] > self.data.High[-2] and self.data.Low[-1] > self.data.Low[-2]:
            fib_low = self.data.Low[-2]
            fib_high = self.data.High[-2]
            fib_50 = fib_low + 0.5 * (fib_high - fib_low)

            if self.data.Low[-1] >= fib_50:
                # Open a long position
                self.buy(sl=fib_low, tp=fib_high)

def backtest_fibonacci_strategy(df, initial_balance=10000):  # Increased initial_balance
    """
    Backtest the Fibonacci strategy using the backtesting package.
    
    Parameters:
        df (DataFrame): Historical data.
        initial_balance (float): Starting balance for the backtest.
    
    Returns:
        Backtest: Backtest object with results.
    """
    # Ensure the DataFrame is sorted
    df.sort_index(inplace=True)

    bt = Backtest(df, FibonacciStrategy, cash=initial_balance, commission=.002)
    stats = bt.run()
    bt.plot()
    return stats

# Example usage:
from fibo_algo import fetch_bybit_testnet_data
df = fetch_bybit_testnet_data("BTCUSDT", "15", 200)
df.sort_index(inplace=True)  # Ensure the DataFrame is sorted
stats = backtest_fibonacci_strategy(df)
print(stats)

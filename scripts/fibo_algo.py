from pybit.unified_trading import HTTP
import pandas as pd
import pandas_ta as ta
import numpy as np
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def fetch_bybit_data(symbol, interval, limit):
    """
    Fetch historical candlestick data from Bybit.
    """
    # Use API key from environment variables if not provided

    # Initialize the HTTP session for Bybit
    session = HTTP(
        testnet=False,  # Use the live Bybit API
        api_key=os.getenv("BYBIT_API_KEY"),
        api_secret=os.getenv("BYBIT_API_SECRET")
    )

    # Fetch historical candlestick data
    response = session.get_kline(
        category="linear",  # For linear contracts
        symbol=symbol,
        interval=interval,
        limit=limit
    )
    
    if response["retCode"] != 0:
        raise Exception(f"Error fetching data: {response['retMsg']}")
    
    # Convert the response to a DataFrame
    data = response["result"]["list"]
    df = pd.DataFrame(data, columns=["open_time", "open", "high", "low", "close", "volume", "turnover"])
    df = df.drop(columns=["turnover"])  # Drop unnecessary columns
    df["datetime"] = pd.to_datetime(pd.to_numeric(df["open_time"]), unit="ms")  # Explicitly cast to numeric
    df.set_index("datetime", inplace=True)
    df = df.astype(float)  # Convert all columns to float
    return df[["open", "high", "low", "close", "volume"]]

def fetch_bybit_testnet_data(symbol, interval, limit):
    """
    Fetch historical candlestick data from Bybit TESTNET.
    """

    # Initialize the HTTP session for Bybit Testnet
    session = HTTP(
        testnet=True,  # Use the Bybit Testnet API
        api_key=os.getenv("BYBIT_TESTNET_API_KEY")
    )

    # Fetch historical candlestick data
    response = session.get_kline(
        category="linear",  # For linear contracts
        symbol=symbol,
        interval=interval,
        limit=limit
    )
    
    if response["retCode"] != 0:
        raise Exception(f"Error fetching data from TESTNET: {response['retMsg']}")

    # Convert the response to a DataFrame
    data = response["result"]["list"]
    df = pd.DataFrame(data, columns=["open_time", "open", "high", "low", "close", "volume", "turnover"])
    df = df.drop(columns=["turnover"])  # Drop unnecessary columns
    
    # Fix the FutureWarning by explicitly casting to numeric
    df["datetime"] = pd.to_datetime(pd.to_numeric(df["open_time"]), unit="ms")
    df.set_index("datetime", inplace=True)
    
    # Rename columns for compatibility with the backtesting library
    df.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    }, inplace=True)
    
    # Convert all columns to float
    df = df.astype(float)
    
    df.sort_index(inplace=True)  # Ensure the index is sorted
    
    return df[["Open", "High", "Low", "Close", "Volume"]]

def run_fibonacci_strategy(df):
    """
    Run the Fibonacci strategy on the given DataFrame.
    """
    # Preprocess data
    df = df[df['volume'] != 0]
    df['RSI'] = ta.rsi(df.close, length=12)
    df['EMA'] = ta.ema(df.close, length=150)

    # Trend detection
    EMAsignal = [0] * len(df)
    candle_time = 15
    for row in range(candle_time, len(df)):
        upt = 1
        dnt = 1
        for i in range(row - candle_time, row + 1):
            if max(df.open.iloc[i], df.close.iloc[i]) >= df.EMA.iloc[i]:
                dnt = 0
            if min(df.open.iloc[i], df.close.iloc[i]) <= df.EMA.iloc[i]:
                upt = 0
        if upt == 1 and dnt == 1:
            EMAsignal[row] = 3
        elif upt == 1:
            EMAsignal[row] = 2
        elif dnt == 1:
            EMAsignal[row] = 1
    df['EMASignal'] = EMAsignal

    # Impulse detection (1.1)
    def detect_impulse(df, row):
        if row < 1:
            return False, None
        first_candle = df.iloc[row - 1]
        second_candle = df.iloc[row]
        if second_candle.high > first_candle.high and second_candle.low > first_candle.low:
            fib_50 = first_candle.low + 0.5 * (first_candle.high - first_candle.low)
            if second_candle.low >= fib_50:
                return True, (first_candle.low, first_candle.high)
        return False, None

    # Position opening and Fibonacci levels (1.2)
    def open_position(df, row, fib_levels):
        entry_levels = [fib_levels[0] + 0.382 * (fib_levels[1] - fib_levels[0]),
                        fib_levels[0] + 0.5 * (fib_levels[1] - fib_levels[0]),
                        fib_levels[0] + 0.618 * (fib_levels[1] - fib_levels[0])]
        tp_levels = [fib_levels[0] + 0.236 * (fib_levels[1] - fib_levels[0]),
                     fib_levels[0] + 0.382 * (fib_levels[1] - fib_levels[0]),
                     fib_levels[1]]
        sl_levels = [entry_levels[0], entry_levels[1], entry_levels[2]]

        for i, entry in enumerate(entry_levels):
            if abs(df.close.iloc[row] - entry) < 0.001:  # Entry condition
                return (entry, tp_levels[i], sl_levels[i])
        return (0, 0, 0)

    # Stop-loss adjustment (1.3)
    def adjust_stop_loss(entry_price, current_price, tp_level):
        if current_price >= tp_level:
            return entry_price  # Move SL to breakeven
        elif current_price <= entry_price * 0.98:  # -2% risk
            return -1  # Close position
        return None

    # Main logic
    signal = [0 for _ in range(len(df))]
    TP = [0 for _ in range(len(df))]
    SL = [0 for _ in range(len(df))]
    active_fib = None

    for row in range(1, len(df)):
        if active_fib is None:
            impulse_detected, fib_levels = detect_impulse(df, row)
            if impulse_detected:
                active_fib = fib_levels
        else:
            entry, tp, sl = open_position(df, row, active_fib)
            if entry:
                signal[row] = 1  # Buy signal
                TP[row] = tp
                SL[row] = sl
                adjusted_sl = adjust_stop_loss(entry, df.close[row], tp)
                if adjusted_sl == -1:
                    signal[row] = 0  # Close position
                    active_fib = None
                elif adjusted_sl is not None:
                    SL[row] = adjusted_sl

    df['signal'] = signal
    df['SL'] = SL
    df['TP'] = TP

    # Return the last signal and associated levels
    latest_signal = df.iloc[-1]
    return {
        "signal": latest_signal['signal'],
        "stop_loss": latest_signal['SL'],
        "take_profit": latest_signal['TP']
    }

def run_fibonacci_strategy_with_bybit(symbol, interval, limit, api_key=None):
    """
    Fetch data from Bybit and run the Fibonacci strategy.
    """
    df = fetch_bybit_data(symbol, interval, limit, api_key)
    return run_fibonacci_strategy(df)

def run_fibonacci_strategy_with_testnet(symbol, interval, limit, api_key=None):
    """
    Fetch data from Bybit TESTNET and run the Fibonacci strategy.
    """
    df = fetch_bybit_testnet_data(symbol, interval, limit, api_key)
    return run_fibonacci_strategy(df)

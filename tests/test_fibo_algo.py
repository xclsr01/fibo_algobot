import os
import pandas as pd
from datetime import datetime, timedelta
from scripts.fibo_algo import run_fibonacci_strategy, fetch_bybit_data
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_run_fibonacci_strategy():
    # Create a sample dataset with a datetime index for testing
    start_date = datetime(2023, 1, 1)
    test_data = {
        "datetime": [start_date + timedelta(days=i) for i in range(5)],
        "open": [1.1, 1.2, 1.3, 1.4, 1.5],
        "high": [1.2, 1.3, 1.4, 1.5, 1.6],
        "low": [1.0, 1.1, 1.2, 1.3, 1.4],
        "close": [1.15, 1.25, 1.35, 1.45, 1.55],
        "volume": [100, 200, 300, 400, 500],
    }
    test_df = pd.DataFrame(test_data)
    test_df.set_index("datetime", inplace=True)

    # Run the strategy function
    result = run_fibonacci_strategy(test_df)
    print(result)

    # Check if the function returns a valid result
    assert result is not None, "The function did not return any result."
    assert "signal" in result, "The result does not contain 'signal'."
    assert "stop_loss" in result, "The result does not contain 'stop_loss'."
    assert "take_profit" in result, "The result does not contain 'take_profit'."

    # Validate the types of the returned values
    assert isinstance(result["signal"], (int, float)), "'signal' should be a number."
    assert isinstance(result["stop_loss"], (int, float)), "'stop_loss' should be a number."
    assert isinstance(result["take_profit"], (int, float)), "'take_profit' should be a number."

def test_fetch_bybit_data():
    """
    Test fetching historical data from Bybit.
    """
    symbol = "BTCUSDT"
    interval = "15"  # 15-minute candles
    limit = 5  # Fetch 5 candles

    # Use API keys from environment variables
    api_key = os.getenv("BYBIT_API_KEY")
    api_secret = os.getenv("BYBIT_API_SECRET")

    df = fetch_bybit_data(symbol, interval, limit, api_key, api_secret)

    # Validate the fetched data
    assert not df.empty, "The fetched data is empty."
    assert all(col in df.columns for col in ["open", "high", "low", "close", "volume"]), \
        "Missing required columns in the fetched data."

def test_fetch_bybit_testnet_data():
    """
    Test fetching historical data from Bybit TESTNET.
    """
    symbol = "BTCUSDT"
    interval = "15"  # 15-minute candles
    limit = 5  # Fetch 5 candles

    # Use API keys from environment variables
    api_key = os.getenv("BYBIT_TESTNET_API_KEY")
    api_secret = os.getenv("BYBIT_TESTNET_API_SECRET")

    df = fetch_bybit_testnet_data(symbol, interval, limit, api_key, api_secret)

    # Validate the fetched data
    assert not df.empty, "The fetched data from TESTNET is empty."
    assert all(col in df.columns for col in ["open", "high", "low", "close", "volume"]), \
        "Missing required columns in the fetched data from TESTNET."

def test_run_fibonacci_strategy_with_testnet():
    """
    Test running the Fibonacci strategy with Bybit TESTNET data.
    """
    symbol = "BTCUSDT"
    interval = "15"  # 15-minute candles
    limit = 5  # Fetch 5 candles

    # Use API keys from environment variables
    api_key = os.getenv("BYBIT_TESTNET_API_KEY")
    api_secret = os.getenv("BYBIT_TESTNET_API_SECRET")

    result = run_fibonacci_strategy_with_testnet(symbol, interval, limit, api_key, api_secret)

    # Validate the result
    assert result is not None, "The function did not return any result."
    assert "signal" in result, "The result does not contain 'signal'."
    assert "stop_loss" in result, "The result does not contain 'stop_loss'."
    assert "take_profit" in result, "The result does not contain 'take_profit'."

    # Validate the types of the returned values
    assert isinstance(result["signal"], (int, float)), "'signal' should be a number."
    assert isinstance(result["stop_loss"], (int, float)), "'stop_loss' should be a number."
    assert isinstance(result["take_profit"], (int, float)), "'take_profit' should be a number."

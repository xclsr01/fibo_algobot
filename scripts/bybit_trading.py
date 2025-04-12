import pandas as pd
from datetime import datetime
from pybit import HTTP
from scripts.fibo_algo import run_fibonacci_strategy

def fetch_bybit_data(client, symbol, interval, limit=200):
    """
    Fetch historical candlestick data from Bybit using pybit.
    """
    response = client.query_kline(symbol=symbol, interval=interval, limit=limit)
    if "ret_code" in response and response["ret_code"] != 0:
        raise Exception(f"Error fetching data: {response.get('ret_msg', 'Unknown error')}")

    data = response["result"]
    df = pd.DataFrame(data)
    df['datetime'] = pd.to_datetime(df['open_time'], unit='s')
    df.rename(columns={
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'volume': 'volume'
    }, inplace=True)
    df.set_index('datetime', inplace=True)
    return df[['open', 'high', 'low', 'close', 'volume']]

def place_bybit_order(client, symbol, side, qty, stop_loss=None, take_profit=None):
    """
    Place an order on Bybit using pybit.
    """
    order_params = {
        "symbol": symbol,
        "side": side,
        "order_type": "Market",
        "qty": qty,
        "time_in_force": "GoodTillCancel",
        "reduce_only": False,
        "close_on_trigger": False,
    }
    if stop_loss:
        order_params["stop_loss"] = stop_loss
    if take_profit:
        order_params["take_profit"] = take_profit

    response = client.place_active_order(**order_params)
    if "ret_code" in response and response["ret_code"] != 0:
        raise Exception(f"Error placing order: {response.get('ret_msg', 'Unknown error')}")
    return response["result"]

def run_bybit_trading(client, symbol, interval, qty):
    """
    Fetch data, run the strategy, and place trades on Bybit using pybit.
    """
    # Fetch historical data
    df = fetch_bybit_data(client, symbol, interval)

    # Run the Fibonacci strategy
    result = run_fibonacci_strategy(df)

    # Check for signals and place orders
    if result["signal"] == 1:  # Sell signal
        place_bybit_order(client, symbol, "Sell", qty, stop_loss=result["stop_loss"], take_profit=result["take_profit"])
    elif result["signal"] == 2:  # Buy signal
        place_bybit_order(client, symbol, "Buy", qty, stop_loss=result["stop_loss"], take_profit=result["take_profit"])

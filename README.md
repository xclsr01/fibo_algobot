# Fibo AlgoBot

## Overview

This project implements an algorithmic trading bot that uses the Fibonacci strategy to trade on the Bybit cryptocurrency exchange. The bot fetches historical market data, analyzes it using the Fibonacci strategy, and places trades based on the generated signals.

## Scripts

### `scripts/bybit_trading.py`

This script contains the main functionality for interacting with the Bybit exchange using the `pybit` library. It includes the following key functions:

1. **`fetch_bybit_data(client, symbol, interval, limit=200)`**  
   Fetches historical candlestick data from Bybit.  
   - **Parameters**:
     - `client`: An instance of the Bybit HTTP client.
     - `symbol`: The trading pair (e.g., "BTCUSDT").
     - `interval`: The candlestick interval (e.g., "1m", "5m").
     - `limit`: The number of candlesticks to fetch (default is 200).
   - **Returns**: A Pandas DataFrame containing the candlestick data with columns: `open`, `high`, `low`, `close`, and `volume`.

2. **`place_bybit_order(client, symbol, side, qty, stop_loss=None, take_profit=None)`**  
   Places a market order on Bybit.  
   - **Parameters**:
     - `client`: An instance of the Bybit HTTP client.
     - `symbol`: The trading pair.
     - `side`: The order side ("Buy" or "Sell").
     - `qty`: The quantity to trade.
     - `stop_loss`: Optional stop-loss price.
     - `take_profit`: Optional take-profit price.
   - **Returns**: The response from the Bybit API containing order details.

3. **`run_bybit_trading(client, symbol, interval, qty)`**  
   The main function that integrates data fetching, strategy execution, and order placement.  
   - **Steps**:
     1. Fetches historical data using `fetch_bybit_data`.
     2. Runs the Fibonacci strategy using `run_fibonacci_strategy` (imported from `scripts/fibo_algo`).
     3. Places a trade based on the strategy's signal:
        - Signal `1`: Places a "Sell" order.
        - Signal `2`: Places a "Buy" order.
   - **Parameters**:
     - `client`: An instance of the Bybit HTTP client.
     - `symbol`: The trading pair.
     - `interval`: The candlestick interval.
     - `qty`: The quantity to trade.

## Requirements

- Python 3.x
- Libraries:
  - `pandas`
  - `pybit`
  - `datetime`

## Usage

1. Set up the Bybit API client using the `pybit` library.
2. Call the `run_bybit_trading` function with the desired parameters (e.g., trading pair, interval, and quantity).
3. The bot will automatically fetch data, analyze it, and place trades based on the Fibonacci strategy.

## Disclaimer

This bot is for educational purposes only. Use it at your own risk. Ensure you understand the risks of algorithmic trading before deploying it in a live trading environment.

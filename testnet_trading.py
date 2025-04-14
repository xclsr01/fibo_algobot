import os
import logging
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
from pybit.unified_trading import WebSocketTrading
from scripts.fibo_algo import run_fibonacci_strategy_with_testnet

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Fetch API key from environment variables
API_KEY = os.getenv("BYBIT_TESTNET_API_KEY")

# Initialize Bybit WebSocket Testnet client
ws_trading = WebSocketTrading(
    testnet=True,
    api_key=API_KEY,
)

def handle_place_order_message(message):
    """
    Handle the response after placing an order.
    """
    order_data = message.get("data", {})
    logger.info(
        f"Order placed: ID={order_data.get('orderId')}, "
        f"Symbol={order_data.get('symbol')}, "
        f"Side={order_data.get('side')}, "
        f"Qty={order_data.get('qty')}, "
        f"Price={order_data.get('price')}, "
        f"Time={datetime.now()}"
    )
    sleep(1)
    # Example: Amend the order
    ws_trading.amend_order(
        handle_amend_order_message,
        category="linear",
        symbol="BTCUSDT",
        order_id=order_data.get("orderId"),
        qty="0.002"
    )
    sleep(1)
    # Example: Cancel the order
    ws_trading.cancel_order(
        handle_cancel_order_message,
        category="linear",
        symbol="BTCUSDT",
        order_id=order_data.get("orderId")
    )

def handle_amend_order_message(message):
    """
    Handle the response after amending an order.
    """
    logger.info(f"Order amended: {message}")

def handle_cancel_order_message(message):
    """
    Handle the response after canceling an order.
    """
    logger.info(f"Order canceled: {message}")

def handle_batch_place_order_message(message):
    """
    Handle the response after placing batch orders.
    """
    logger.info(f"Batch orders placed: {message}")

def trade_on_testnet(symbol, interval, limit, qty):
    """
    Continuously fetch data from Bybit Testnet, run the Fibonacci strategy, and trade based on signals.
    """
    logger.info("Starting trading on Bybit Testnet...")
    while True:
        try:
            logger.info("Analyzing market data...")
            # Run the Fibonacci strategy
            result = run_fibonacci_strategy_with_testnet(symbol, interval, limit)

            # Extract signal, stop loss, and take profit
            signal = result["signal"]
            stop_loss = result["stop_loss"]
            take_profit = result["take_profit"]

            logger.info(f"Strategy result: Signal={signal}, Stop Loss={stop_loss}, Take Profit={take_profit}")

            if signal == 1:  # Buy signal
                logger.info("Buy signal detected. Placing a buy order...")
                ws_trading.place_order(
                    handle_place_order_message,
                    category="linear",
                    symbol=symbol,
                    side="Buy",
                    orderType="Market",
                    qty=str(qty),
                    timeInForce="GTC"
                )
            elif signal == 2:  # Sell signal
                logger.info("Sell signal detected. Placing a sell order...")
                ws_trading.place_order(
                    handle_place_order_message,
                    category="linear",
                    symbol=symbol,
                    side="Sell",
                    orderType="Market",
                    qty=str(qty),
                    timeInForce="GTC"
                )
            else:
                logger.info("No valid signal detected. No action taken.")

            # Wait before the next iteration
            sleep(60)  # Wait for 1 minute before fetching new data
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            sleep(60)  # Wait for 1 minute before retrying

if __name__ == "__main__":
    # Define trading parameters
    SYMBOL = "BTCUSDT"  # Trading pair
    INTERVAL = "15"     # Timeframe in minutes
    LIMIT = 200         # Number of candlesticks to fetch
    QTY = 0.01          # Order quantity

    # Start trading on Bybit Testnet
    trade_on_testnet(SYMBOL, INTERVAL, LIMIT, QTY)

from backtesting import Strategy
import pandas_ta as ta
import numpy as np


def ema(data, length):
    """
    Calculate Exponential Moving Average (EMA).
    """
    alpha = 2 / (length + 1)
    ema = np.empty_like(data)
    ema[0] = data[0]  # Initialize with the first value
    for i in range(1, len(data)):
        ema[i] = alpha * data[i] + (1 - alpha) * ema[i - 1]
    return ema

def rsi(data, length):
    """
    Calculate Relative Strength Index (RSI).
    """
    deltas = np.diff(data)
    gains = np.maximum(deltas, 0)
    losses = -np.minimum(deltas, 0)
    avg_gain = np.empty_like(data)
    avg_loss = np.empty_like(data)
    avg_gain[:length] = np.mean(gains[:length])
    avg_loss[:length] = np.mean(losses[:length])
    for i in range(length, len(data)):
        avg_gain[i] = (avg_gain[i - 1] * (length - 1) + gains[i - 1]) / length
        avg_loss[i] = (avg_loss[i - 1] * (length - 1) + losses[i - 1]) / length
    rs = avg_gain[length:] / avg_loss[length:]
    rsi = np.zeros_like(data)
    rsi[length:] = 100 - (100 / (1 + rs))
    return rsi

#TODO: взять логику из алгоритма ютуб видео, который очень хорошо отрабатывает
#TODO: реализовать работу в realtime
#TODO: добавить логику по определению импульса, чтобы не открывать позицию в боковике
#TODO: добавить логику по определению коррекции, чтобы не открывать позицию в импульсе
#TODO: добавить логику по определению уровня, чтобы не открывать позицию в боковике
class FibonacciStrategy(Strategy):
    """
    Implements the Fibonacci strategy for Bybit BTCUSDT trades.
    """
    def init(self):
        # Add EMA and RSI indicators using self.I
        self.ema = self.I(ema, self.data.Close, length=150)
        self.rsi = self.I(rsi, self.data.Close, length=12)
        self.active_fib = None  # Track active Fibonacci grid
        self.entry_price = None  # Track entry price for stop-loss adjustments
        self.max_drawdown = 0  # Track maximum drawdown

    def detect_impulse(self):
        """
        Detects an impulse movement based on two consecutive candles.
        """
        if len(self.data) < 2:
            return False, None

        first_candle = {
            "high": self.data.High[-2],
            "low": self.data.Low[-2]
        }
        second_candle = {
            "high": self.data.High[-1],
            "low": self.data.Low[-1]
        }

        # Tightened impulse criteria
        impulse_detected = (
            second_candle["high"] > first_candle["high"] and
            second_candle["low"] >= first_candle["low"] + 0.5 * (first_candle["high"] - first_candle["low"])
        )

        if impulse_detected:
            fib_levels = {
                "low": first_candle["low"],
                "high": first_candle["high"],
                "50%": first_candle["low"] + 0.5 * (first_candle["high"] - first_candle["low"]),
                "61.8%": first_candle["low"] + 0.618 * (first_candle["high"] - first_candle["low"]),
                "78.6%": first_candle["low"] + 0.786 * (first_candle["high"] - first_candle["low"]),
            }
            return True, fib_levels
        return False, None

    def open_position(self, fib_levels):
        """
        Opens a position based on corrections to key Fibonacci levels.
        """
        entry_levels = [
            fib_levels["low"] + 0.236 * (fib_levels["high"] - fib_levels["low"]),
            fib_levels["low"] + 0.382 * (fib_levels["high"] - fib_levels["low"]),
            fib_levels["low"] + 0.5 * (fib_levels["high"] - fib_levels["low"]),
            fib_levels["low"] + 0.618 * (fib_levels["high"] - fib_levels["low"]),
            fib_levels["low"] + 0.786 * (fib_levels["high"] - fib_levels["low"])
        ]
        tp_levels = [
            fib_levels["high"]  # Use the same take-profit level for all entries
        ] * len(entry_levels)  # Match the length of entry_levels
        sl_levels = [fib_levels["low"]] * len(entry_levels)

        for i, entry in enumerate(entry_levels):
            if self.data.Close[-1] > self.ema[-1]:  # Confirm uptrend
                if abs(self.data.Close[-1] - entry) < 0.02 * entry:  # Allow a 2% margin
                    print(f"Buy signal triggered at level {entry}")
                    print(f"SL: {sl_levels[i]}, LIMIT: {self.data.Close[-1]}, TP: {tp_levels[i]}")
                    
                    # Validate SL, LIMIT, and TP order
                    if sl_levels[i] < self.data.Close[-1] < tp_levels[i]:
                        capital = self._broker.equity  # Use self._broker.equity instead of self._broker.cash
                        risk_per_trade = 0.02 * capital  # 2% risk
                        stop_loss_distance = abs(self.data.Close[-1] - sl_levels[i])
                        position_size = risk_per_trade / stop_loss_distance

                        # Ensure position_size is valid
                        if position_size <= 0:
                            print(f"Invalid position size: {position_size}. Skipping order.")
                            continue
                        if position_size < 1:
                            position_size = max(position_size, 0.01)  # Minimum fraction of equity
                        else:
                            position_size = round(position_size)  # Whole number of units

                        self.buy(sl=sl_levels[i], tp=tp_levels[i], size=position_size)
                        self.entry_price = entry  # Track entry price
                        return True
                    else:
                        print(f"Invalid order: SL ({sl_levels[i]}) < LIMIT ({self.data.Close[-1]}) < TP ({tp_levels[i]})")

        # Check for a buy signal at the 50% Fibonacci level
        if abs(self.data.Close[-1] - fib_levels["50%"]) < 0.01 * fib_levels["50%"]:
            sl = fib_levels["low"]
            tp = fib_levels["high"]
            if sl < self.data.Close[-1] < tp:
                capital = self._broker.equity  # Use self._broker.equity instead of self._broker.cash
                risk_per_trade = 0.02 * capital  # 2% risk
                stop_loss_distance = abs(self.data.Close[-1] - sl)
                position_size = risk_per_trade / stop_loss_distance

                # Ensure position_size is valid
                if position_size <= 0:
                    print(f"Invalid position size: {position_size}. Skipping order.")
                    return False
                if position_size < 1:
                    position_size = max(position_size, 0.01)  # Minimum fraction of equity
                else:
                    position_size = round(position_size)  # Whole number of units

                self.buy(sl=sl, tp=tp, size=position_size)
                print(f"Buy signal triggered at level {fib_levels['50%']}")
            else:
                print(f"Invalid levels: SL ({sl}) < LIMIT ({self.data.Close[-1]}) < TP ({tp})")
        return False

    def adjust_stop_loss(self, tp_level):
        """
        Adjusts the stop-loss after reaching the nearest level.
        """
        if self.data.Close[-1] >= tp_level:
            print("Take-profit level reached. Moving stop-loss to breakeven.")
            self.position.sl = self.entry_price  # Move stop-loss to breakeven
        elif self.data.Close[-1] <= self.entry_price * 0.98:  # -2% risk
            print("Stop-loss level reached. Closing position.")
            self.position.close()  # Close position at stop-loss

    def next(self):
        if self.active_fib is None:
            impulse_detected, fib_levels = self.detect_impulse()
            if impulse_detected:
                self.active_fib = fib_levels
                print(f"Impulse detected: {self.active_fib}")
        else:
            # Attempt to open a position
            position_opened = self.open_position(self.active_fib)
            if position_opened:
                print("Position opened")
            elif not self.position:
                # Reset Fibonacci levels if no position is open
                self.active_fib = None
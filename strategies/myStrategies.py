from baseStrategy import BaseStrategy
from collections import deque
import numpy as np

class MovingAverageCrossoverStrategy(BaseStrategy):
    def __init__(self, short_window=5, long_window=20, name="MA_Crossover"):
        super().__init__(name)
        self.short_window = short_window
        self.long_window = long_window
        
        # Deques to store recent close prices
        self.short_prices = deque(maxlen=short_window)
        self.long_prices  = deque(maxlen=long_window)

    def on_bar(self, symbol: str, bar_data: dict) -> str:
        close_price = bar_data['close']
        self.short_prices.append(close_price)
        self.long_prices.append(close_price)

        # If we don't have enough data yet, just hold
        if len(self.short_prices) < self.short_window or len(self.long_prices) < self.long_window:
            return "HOLD"
        
        short_ma = np.mean(self.short_prices)
        long_ma = np.mean(self.long_prices)

        if short_ma > long_ma:
            return "BUY"
        elif short_ma < long_ma:
            return "SELL"
        else:
            return "HOLD"

class BreakoutStrategy(BaseStrategy):
    def __init__(self, lookback=20, name="Breakout_Strategy"):
        super().__init__(name)
        self.lookback = lookback
        
        self.highs = deque(maxlen=lookback)
        self.lows  = deque(maxlen=lookback)

    def on_bar(self, symbol: str, bar_data: dict) -> str:
        self.highs.append(bar_data['high'])
        self.lows.append(bar_data['low'])

        if len(self.highs) < self.lookback:
            return "HOLD"

        current_close = bar_data['close']
        highest_high = max(self.highs)
        lowest_low = min(self.lows)

        if current_close > highest_high:
            return "BUY"
        elif current_close < lowest_low:
            return "SELL"
        else:
            return "HOLD"

class RSIStrategy(BaseStrategy):
    def __init__(self, period=14, rsi_buy=30, rsi_sell=70, name="RSI_Strategy"):
        super().__init__(name)
        self.period = period
        self.rsi_buy = rsi_buy
        self.rsi_sell = rsi_sell
        
        self.prices = deque(maxlen=period+1)
        self.last_rsi = None

    def on_bar(self, symbol: str, bar_data: dict) -> str:
        close_price = bar_data['close']
        self.prices.append(close_price)

        # Not enough data for RSI
        if len(self.prices) < self.period+1:
            return "HOLD"

        # Compute price differences
        gains = 0.0
        losses = 0.0
        for i in range(1, len(self.prices)):
            diff = self.prices[i] - self.prices[i-1]
            if diff >= 0:
                gains += diff
            else:
                losses += abs(diff)

        avg_gain = gains / self.period
        avg_loss = losses / self.period if losses != 0 else 1e-9  # avoid zero-div
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        self.last_rsi = rsi  # store for debugging

        # Basic RSI logic: Buy if oversold (< rsi_buy), Sell if overbought (> rsi_sell)
        if rsi < self.rsi_buy:
            return "BUY"
        elif rsi > self.rsi_sell:
            return "SELL"
        else:
            return "HOLD"

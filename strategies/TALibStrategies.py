import numpy as np
import talib
from collections import deque
from .baseStrategy import BaseStrategy

class BollingerStrategy(BaseStrategy):
    def __init__(self, period=20, nbdev=2.0, name="Bollinger_Strategy"):
        super().__init__(name)
        self.period = period
        self.nbdev = nbdev
        self.close_prices = deque(maxlen=period*2)  # store some extra

    def on_bar(self, symbol: str, bar_data: dict) -> str:
        close_price = bar_data["close"]
        self.close_prices.append(close_price)

        # Not enough data
        if len(self.close_prices) < self.period:
            return "HOLD"

        prices = np.array(self.close_prices, dtype=float)

        # TA-Lib BBANDS
        upper, middle, lower = talib.BBANDS(
            prices,
            timeperiod=self.period,
            nbdevup=self.nbdev,
            nbdevdn=self.nbdev,
            matype=0  # 0 = simple moving average
        )

        last_close = prices[-1]
        last_upper = upper[-1]
        last_lower = lower[-1]

        # Simple logic:
        if last_close < last_lower:
            return "BUY"
        elif last_close > last_upper:
            return "SELL"
        else:
            return "HOLD"

class MACDStrategy(BaseStrategy):
    def __init__(self, fast=12, slow=26, signal=9, name="MACD_Strategy"):
        super().__init__(name)
        self.prices = deque()
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def on_bar(self, symbol: str, bar_data: dict) -> str:
        self.prices.append(bar_data["close"])
        
        # If not enough data to calculate MACD, hold
        if len(self.prices) < self.slow:
            return "HOLD"

        arr = np.array(self.prices, dtype=float)
        macd, macd_signal, macd_hist = talib.MACD(
            arr,
            fastperiod=self.fast,
            slowperiod=self.slow,
            signalperiod=self.signal
        )

        # get latest
        last_macd = macd[-1]
        last_signal = macd_signal[-1]

        if last_macd > last_signal:
            return "BUY"
        elif last_macd < last_signal:
            return "SELL"
        else:
            return "HOLD"

class StochasticStrategy(BaseStrategy):
    def __init__(self, fastk_period=14, slowk_period=3, slowd_period=3, name="Stoch_Strategy"):
        super().__init__(name)
        self.highs = deque()
        self.lows = deque()
        self.closes = deque()
        self.fastk_period = fastk_period
        self.slowk_period = slowk_period
        self.slowd_period = slowd_period

    def on_bar(self, symbol: str, bar_data: dict) -> str:
        self.highs.append(bar_data["high"])
        self.lows.append(bar_data["low"])
        self.closes.append(bar_data["close"])

        # need at least fastk_period bars
        if len(self.closes) < self.fastk_period:
            return "HOLD"

        highs_arr = np.array(self.highs, dtype=float)
        lows_arr = np.array(self.lows, dtype=float)
        closes_arr = np.array(self.closes, dtype=float)

        # Stochastic
        slowk, slowd = talib.STOCH(
            highs_arr,
            lows_arr,
            closes_arr,
            fastk_period=self.fastk_period,
            slowk_period=self.slowk_period,
            slowk_matype=0,
            slowd_period=self.slowd_period,
            slowd_matype=0
        )

        k_value = slowk[-1]
        d_value = slowd[-1]

        if k_value < 20 and d_value < 20:
            return "BUY"
        elif k_value > 80 and d_value > 80:
            return "SELL"
        else:
            return "HOLD"

class ParabolicSARStrategy(BaseStrategy):
    def __init__(self, acceleration=0.02, maximum=0.2, name="PSAR_Strategy"):
        super().__init__(name)
        self.highs = deque()
        self.lows = deque()
        self.acceleration = acceleration
        self.maximum = maximum

    def on_bar(self, symbol: str, bar_data: dict) -> str:
        self.highs.append(bar_data["high"])
        self.lows.append(bar_data["low"])

        if len(self.highs) < 2:  # need at least 2-3 bars
            return "HOLD"

        hs = np.array(self.highs, dtype=float)
        ls = np.array(self.lows, dtype=float)

        # compute parabolic SAR
        psar = talib.SAR(hs, ls, acceleration=self.acceleration, maximum=self.maximum)
        last_psar = psar[-1]
        last_close = bar_data["close"]

        # if psar below close => uptrend => buy
        if last_psar < last_close:
            return "BUY"
        else:
            return "SELL"  # or "HOLD"

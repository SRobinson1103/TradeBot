from abc import ABC, abstractmethod

# An abstract base class for all trading strategies.
# Each strategy must implement `on_bar()`, 
# and optionally can track its own indicators or internal state.
class BaseStrategy(ABC):
    def __init__(self, name: str):
        self.name = name

    # Called whenever a new bar arrives for `symbol`.
    #          {
    #            'timestamp': datetime,
    #            'open': float,
    #           'high': float,
    #           'low': float,
    #           'close': float,
    #           'volume': float,
    #           ...
    #         }
    # Return a string signal: "BUY", "SELL", or "HOLD".
    @abstractmethod
    def on_bar(self, symbol: str, bar_data: dict) -> str:
        pass

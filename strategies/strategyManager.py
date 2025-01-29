import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .ensembleStrategy import EnsembleStrategy
from .TALibStrategies import BollingerStrategy, MACDStrategy, ParabolicSARStrategy, StochasticStrategy

boll = BollingerStrategy(period=20, nbdev=2)
macd = MACDStrategy()
para = ParabolicSARStrategy()
stoch = StochasticStrategy()
ensemble = EnsembleStrategy([boll, macd, para, stoch])

async def on_stock_bar(bar):
    print("OnStockBar")
    bar_dict = {
        'ts' : bar.timestamp,
        'open': bar.open,
        'high': bar.high,
        'low': bar.low,
        'close': bar.close,
        'volume': bar.volume
    }
    signal = await ensemble.on_bar(bar.symbol, bar_dict)
    print("Signal:", signal)
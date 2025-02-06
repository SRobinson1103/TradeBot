import logging
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, OrderSide, TimeInForce
from .ensembleStrategy import EnsembleStrategy
from .TALibStrategies import BollingerStrategy, MACDStrategy, ParabolicSARStrategy, StochasticStrategy

from config import API_KEY, SECRET_KEY

boll = BollingerStrategy(period=20, nbdev=2)
macd = MACDStrategy()
para = ParabolicSARStrategy()
stoch = StochasticStrategy()
ensemble = EnsembleStrategy([boll, macd, para, stoch])

async def on_stock_bar(bar):
    bar_dict = {
        'ts' : bar.timestamp,
        'open': bar.open,
        'high': bar.high,
        'low': bar.low,
        'close': bar.close,
        'volume': bar.volume
    }
    signal = ensemble.on_bar(bar.symbol, bar_dict)
    await execute_signal(signal, bar.symbol)
    
    
    

# Create a global or class-level trading client
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

logging.basicConfig(
    level=logging.INFO,           # or DEBUG, WARNING, ERROR, etc.
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Receives a signal and places a market order if needed.
# By default, it buys/sells `qty` shares/contracts.
async def execute_signal(signal: str, symbol: str, qty: int = 1):
    # Do nothing
    if signal == "HOLD":
        logging.info(f"[{symbol}] HOLD signal received, no order placed.")
        return

    # prepare the order
    if signal == "BUY":
        side = OrderSide.BUY
    elif signal == "SELL":
        side = OrderSide.SELL
    else:
        logging.warning(f"Unknown signal: {signal}")
        return

    order_data = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        time_in_force=TimeInForce.DAY
    )

    try:
        logging.info(f"Placing {signal} order for {symbol}, qty={qty}")
        order = trading_client.submit_order(order_data=order_data)
        logging.info(f"Order submitted: {order}")
    except Exception as e:
        logging.error(f"Error placing {signal} order for {symbol}: {e}")
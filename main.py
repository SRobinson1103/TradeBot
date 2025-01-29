import asyncio
import threading
import strategies.strategyManager as sm

from alpaca.data.live import StockDataStream
from config import API_KEY, SECRET_KEY, STOCK_SYMBOLS_FILE

stock_symbols = None
with open(STOCK_SYMBOLS_FILE) as f:
    stock_symbols = [line.strip() for line in f]
    
stock_stream = StockDataStream(API_KEY, SECRET_KEY)
stock_stream.subscribe_bars(sm.on_stock_bar, *stock_symbols)
print(f"Subscribed to: {stock_symbols}")
       
def run_stock_stream():
    stock_stream.run()
        
async def start():
    stock_thread = threading.Thread(target=run_stock_stream, daemon=True)
    stock_thread.start()
    
    try:
        while True:
            print("waiting")
            await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
         print("KeyboardInterrupt received. Shutting down...")
    finally:
        stock_stream.stop()
        stock_thread.join()
        print("Stream stopped.") 
        
if __name__ == "__main__":
    asyncio.run(start())
    
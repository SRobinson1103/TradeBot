import asyncio
import os
import sys
import threading
import time

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alpaca.data.live import StockDataStream
from databaseQueries import on_stock_bar, init_db_pool, close_db_pool, flush_buffers
from config import API_KEY, SECRET_KEY, ALPACA_PAPER_ENDPOINT, STOCK_SYMBOLS_FILE

stock_symbols = None

with open(STOCK_SYMBOLS_FILE) as f:
    stock_symbols = [line.strip() for line in f]
    
stock_stream = StockDataStream(API_KEY, SECRET_KEY)
stock_stream.subscribe_bars(on_stock_bar, *stock_symbols)

# run on a separate thread
def run_stock_stream():
    stock_stream.run()

# coroutine
async def main():
    await init_db_pool()

    # Start threads
    stock_thread = threading.Thread(target=run_stock_stream, daemon=True)
    stock_thread.start()
    
    # Keep main thread alive until user interrupts (Ctrl + C)
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
         print("KeyboardInterrupt received. Shutting down...")
    finally:
        stock_stream.stop()
        stock_thread.join()
        await flush_buffers()
        await close_db_pool()
        print("Stream stopped, thread joined, DB closed.")

if __name__ == "__main__":
    asyncio.run(main())
    
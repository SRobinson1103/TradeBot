import asyncio
import os
import sys
import threading

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alpaca.data.live import CryptoDataStream
from .databaseQueries import on_crypto_bar, init_db_pool, close_db_pool, flush_buffers
from config import API_KEY, SECRET_KEY, CRYPTO_SYMBOLS_FILE

crypto_symbols = None
with open(CRYPTO_SYMBOLS_FILE) as f:
    crypto_symbols = [line.strip() for line in f]
    
crypto_stream = CryptoDataStream(API_KEY, SECRET_KEY)
crypto_stream.subscribe_bars(on_crypto_bar, *crypto_symbols)

# run on a separate thread
def run_crypto_stream():
    crypto_stream.run()

# coroutine
async def start():
    await init_db_pool()

    stock_thread = threading.Thread(target=run_crypto_stream, daemon=True)
    stock_thread.start()
    
    # Keep main thread alive until user interrupts (Ctrl + C)
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
         print("KeyboardInterrupt received. Shutting down...")
    finally:
        crypto_stream.stop()
        stock_thread.join()
        await flush_buffers()
        await close_db_pool()
        print("Stream stopped, thread joined, DB closed.")

#if __name__ == "__main__":
#    asyncio.run(start())
    
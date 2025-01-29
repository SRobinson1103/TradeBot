import asyncio
import sys
import os
import datetime as dt
import pandas

# Add project root to sys.path, if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alpaca.data import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest, TimeFrame

from config import API_KEY, SECRET_KEY, ALPACA_PAPER_ENDPOINT, STOCK_SYMBOLS_FILE, CRYPTO_SYMBOLS_FILE
import databaseQueries as dbq

crypto_symbols = None
stock_symbols = None

with open(CRYPTO_SYMBOLS_FILE) as f:
    crypto_symbols = [line.strip() for line in f]
    
with open(STOCK_SYMBOLS_FILE) as f:
    stock_symbols = [line.strip() for line in f]

# Ingest historical STOCK data for the date range [start_date, end_date].
async def ingest_stocks(start_date, end_date):
    stock_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

    request_params = StockBarsRequest(
        symbol_or_symbols=stock_symbols,
        timeframe=TimeFrame.Minute,
        start=start_date,
        end=end_date,
        limit=10000
    )

    bars = stock_client.get_stock_bars(request_params)

    df = bars.df.reset_index()
    await dbq.insert_df_to_db(df, False)
    print(f"Finished ingesting stock data for {len(stock_symbols)} symbols from {start_date} to {end_date}.")
    print(f"Number of symbols ingeste is {df.shape[0]}.")

# Ingest historical CRYPTO data for the date range [start_date, end_date].
async def ingest_crypto(start_date, end_date):
    crypto_client = CryptoHistoricalDataClient(API_KEY, SECRET_KEY)

    request_params = CryptoBarsRequest(
        symbol_or_symbols=crypto_symbols,
        timeframe=TimeFrame.Minute,
        start=start_date,
        end=end_date,
        limit=10000
    )

    bars = crypto_client.get_crypto_bars(request_params)

    df = bars.df.reset_index()
    await dbq.insert_df_to_db(df, True)
    print(f"Finished ingesting crypto data for {len(crypto_symbols)} symbols from {start_date} to {end_date}.")
    print(f"Number of symbols ingester is {df.shape[0]}.")

async def main():
    await dbq.init_db_pool()

    # Free version of alpaca is 15 minutes slow
    end_date = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=15)
    start_date = end_date - dt.timedelta(days=14)

    await ingest_stocks(start_date, end_date)
    await ingest_crypto(start_date, end_date)

    await dbq.close_db_pool()

if __name__ == "__main__":
    asyncio.run(main())

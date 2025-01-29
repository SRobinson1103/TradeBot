import asyncpg
import psycopg2
import pandas

from config import DB_HOST, DB_NAME, DB_PASS, DB_USER

pool = None  # will hold the connection pool

# initialization
async def init_db_pool():
    global pool
    pool = await asyncpg.create_pool(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        min_size=1, 
        max_size=5
    )

# termination
async def close_db_pool():
    global pool
    if pool is not None:
        await pool.close()
        pool = None
        
# insert an entire dataframe
async def insert_df_to_db(df:pandas.DataFrame, crypto:bool):
    query = None
    if crypto:
        query = """
            INSERT INTO crypto_bars (time, symbol, open, high, low, close, volume)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (time, symbol) DO NOTHING
        """
    else:        
        query = """
            INSERT INTO stock_bars (time, symbol, open, high, low, close, volume)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (time, symbol) DO NOTHING
        """

    for index, row in df.iterrows():
        symbol = row['symbol']
        ts = row['timestamp']
        o = row['open']
        h = row['high']
        l = row['low']
        c = row['close']
        v = row['volume']

    async with pool.acquire() as conn:
        await conn.execute(query, ts, symbol, o, h, l, c, v)
    
# Insert a single bar asynchronously
async def insert_bar_asyncpg(bar, crypto:bool):
    # parse bar
    ts = bar.timestamp
    symbol = bar.symbol
    o = bar.open
    h = bar.high
    l = bar.low
    c = bar.close
    v = bar.volume

    query = None
    if crypto:        
        query = """
            INSERT INTO crypto_bars (time, symbol, open, high, low, close, volume)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (time, symbol) DO NOTHING
        """
    else:
        query = """
            INSERT INTO stock_bars (time, symbol, open, high, low, close, volume)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (time, symbol) DO NOTHING
        """

    async with pool.acquire() as conn:
        await conn.execute(query, ts, symbol, o, h, l, c, v)
        
   
batch_size = 100 # amount to store until INSERT
stock_bar_buffer = []
crypto_bar_buffer = []

# Add a stock bar to the stock buffer
# Insert all bars in the buffer if the max size is reached
async def on_stock_bar(bar):
    print("Adding stock bar.: ", bar)
    global stock_bar_buffer
    stock_bar_buffer.append(bar)

    if len(stock_bar_buffer) >= batch_size:
        await flush_bars(stock_bar_buffer, crypto=False)
        bar_buffer = []
    
# Add a crypto bar to the crypto buffer
# Insert all bars in the buffer if the max size is reached
async def on_crypto_bar(bar):
    print("Adding crypto bar.: ", bar)
    global crypto_bar_buffer
    crypto_bar_buffer.append(bar)

    if len(crypto_bar_buffer) >= batch_size:
        await flush_bars(crypto_bar_buffer, crypto=True)
        bar_buffer = []

# Insert all bars from the buffer into their appropriate table
async def flush_bars(bars, crypto:bool):
    query = ""
    if crypto:        
        query = """
            INSERT INTO crypto_bars (time, symbol, open, high, low, close, volume)
            VALUES 
        """
    else:
        query = """
            INSERT INTO stock_bars (time, symbol, open, high, low, close, volume)
            VALUES 
        """
        
    placeholders = []
    values = []
    for i, bar in enumerate(bars):
        placeholders.append(f"(${7 * i + 1}, ${7 * i + 2}, ${7 * i + 3}, ${7 * i + 4}, ${7 * i + 5}, ${7 * i + 6}, ${7 * i + 7})")
        values.extend([
            bar.timestamp,
            bar.symbol,
            bar.open,
            bar.high,
            bar.low,
            bar.close,
            int(bar.volume)
        ])

    query += ",".join(placeholders)
    query += " ON CONFLICT (time, symbol) DO NOTHING"

    async with pool.acquire() as conn:
        await conn.execute(query, *values)

async def flush_buffers():
    global stock_bar_buffer
    global crypto_bar_buffer
    
    if len(stock_bar_buffer) > 0:
        await flush_bars(stock_bar_buffer, crypto=False)
        stock_bar_buffer = []
        
    if len(crypto_bar_buffer) > 0:
        await flush_bars(crypto_bar_buffer, crypto=True)
        crypto_bar_buffer = []

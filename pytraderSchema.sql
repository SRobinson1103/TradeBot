-- run once to create tables

-- For stocks
CREATE TABLE IF NOT EXISTS stock_bars (
    time TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume DOUBLE PRECISION,
    PRIMARY KEY (time, symbol)
);

SELECT create_hypertable('stock_bars', 'time', if_not_exists => TRUE, migrate_data => TRUE);

-- For crypto:
CREATE TABLE IF NOT EXISTS crypto_bars (
    time TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume DOUBLE PRECISION,
    PRIMARY KEY (time, symbol)
);

SELECT create_hypertable('crypto_bars', 'time', if_not_exists => TRUE, migrate_data => TRUE);

-- Index on symbol
CREATE INDEX IF NOT EXISTS idx_symbol_stock_bars ON stock_bars(symbol);
CREATE INDEX IF NOT EXISTS idx_symbol_crypto_bars ON crypto_bars(symbol);

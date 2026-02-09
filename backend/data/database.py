"""
SQLite Database Module
Handles all database operations for the stock analysis platform.
"""
import sqlite3
from datetime import datetime
from pathlib import Path
import sys

# Add parent to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DB_PATH


def get_connection():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with all required tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Stocks table - master list of tracked stocks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            sector TEXT,
            industry TEXT,
            added_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Prices table - daily OHLCV data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            adj_close REAL,
            volume INTEGER,
            UNIQUE(symbol, date),
            FOREIGN KEY (symbol) REFERENCES stocks(symbol)
        )
    ''')
    
    # Indicators table - calculated technical indicators
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            rsi REAL,
            roc_5 REAL,
            roc_10 REAL,
            roc_20 REAL,
            atr REAL,
            sma_20 REAL,
            sma_50 REAL,
            macd REAL,
            macd_signal REAL,
            macd_hist REAL,
            bb_upper REAL,
            bb_middle REAL,
            bb_lower REAL,
            relative_volume REAL,
            relative_strength_5 REAL,
            relative_strength_10 REAL,
            relative_strength_20 REAL,
            momentum_score REAL,
            UNIQUE(symbol, date),
            FOREIGN KEY (symbol) REFERENCES stocks(symbol)
        )
    ''')
    
    # Signals table - generated recommendations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            signal_type TEXT NOT NULL,
            momentum_score REAL,
            rationale TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, date),
            FOREIGN KEY (symbol) REFERENCES stocks(symbol)
        )
    ''')
    
    # Nifty history table - benchmark data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nifty_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER
        )
    ''')
    
    # Create indexes for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_prices_symbol_date ON prices(symbol, date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_indicators_symbol_date ON indicators(symbol, date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_date ON signals(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_nifty_date ON nifty_history(date)')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


def insert_stock(symbol: str, name: str = None, sector: str = None, industry: str = None):
    """Insert or update a stock in the master list."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO stocks (symbol, name, sector, industry)
        VALUES (?, ?, ?, ?)
    ''', (symbol, name, sector, industry))
    conn.commit()
    conn.close()


def insert_price_data(symbol: str, data: list):
    """
    Insert price data for a stock.
    data: list of dicts with keys: date, open, high, low, close, adj_close, volume
    """
    conn = get_connection()
    cursor = conn.cursor()
    for row in data:
        cursor.execute('''
            INSERT OR REPLACE INTO prices (symbol, date, open, high, low, close, adj_close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, row['date'], row['open'], row['high'], row['low'], 
              row['close'], row['adj_close'], row['volume']))
    conn.commit()
    conn.close()


def insert_indicators(symbol: str, date: str, indicators: dict):
    """Insert calculated indicators for a stock on a specific date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO indicators 
        (symbol, date, rsi, roc_5, roc_10, roc_20, atr, sma_20, sma_50,
         macd, macd_signal, macd_hist, bb_upper, bb_middle, bb_lower,
         relative_volume, relative_strength_5, relative_strength_10, 
         relative_strength_20, momentum_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (symbol, date, 
          indicators.get('rsi'), indicators.get('roc_5'), indicators.get('roc_10'),
          indicators.get('roc_20'), indicators.get('atr'), indicators.get('sma_20'),
          indicators.get('sma_50'), indicators.get('macd'), indicators.get('macd_signal'),
          indicators.get('macd_hist'), indicators.get('bb_upper'), indicators.get('bb_middle'),
          indicators.get('bb_lower'), indicators.get('relative_volume'),
          indicators.get('relative_strength_5'), indicators.get('relative_strength_10'),
          indicators.get('relative_strength_20'), indicators.get('momentum_score')))
    conn.commit()
    conn.close()


def insert_signal(symbol: str, date: str, signal_type: str, score: float, rationale: str):
    """Insert a signal recommendation."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO signals (symbol, date, signal_type, momentum_score, rationale)
        VALUES (?, ?, ?, ?, ?)
    ''', (symbol, date, signal_type, score, rationale))
    conn.commit()
    conn.close()


def insert_nifty_data(data: list):
    """Insert Nifty 50 benchmark data."""
    conn = get_connection()
    cursor = conn.cursor()
    for row in data:
        cursor.execute('''
            INSERT OR REPLACE INTO nifty_history (date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (row['date'], row['open'], row['high'], row['low'], row['close'], row['volume']))
    conn.commit()
    conn.close()


def get_stock_prices(symbol: str, days: int = 60) -> list:
    """Get recent price data for a stock."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM prices 
        WHERE symbol = ? 
        ORDER BY date DESC 
        LIMIT ?
    ''', (symbol, days))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_stocks() -> list:
    """Get all tracked stocks."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM stocks ORDER BY symbol')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_latest_indicators(limit: int = 500) -> list:
    """Get latest indicators for all stocks (most recent date per stock)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.*, s.name, s.sector
        FROM indicators i
        JOIN stocks s ON i.symbol = s.symbol
        WHERE i.date = (SELECT MAX(date) FROM indicators)
        ORDER BY i.momentum_score DESC
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_stock_indicators(symbol: str, days: int = 30) -> list:
    """Get indicator history for a specific stock."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM indicators 
        WHERE symbol = ? 
        ORDER BY date DESC 
        LIMIT ?
    ''', (symbol, days))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_latest_signals(date: str = None) -> list:
    """Get signals for a specific date (defaults to latest)."""
    conn = get_connection()
    cursor = conn.cursor()
    if date:
        cursor.execute('''
            SELECT sg.*, s.name, s.sector
            FROM signals sg
            JOIN stocks s ON sg.symbol = s.symbol
            WHERE sg.date = ?
            ORDER BY sg.momentum_score DESC
        ''', (date,))
    else:
        cursor.execute('''
            SELECT sg.*, s.name, s.sector
            FROM signals sg
            JOIN stocks s ON sg.symbol = s.symbol
            WHERE sg.date = (SELECT MAX(date) FROM signals)
            ORDER BY sg.momentum_score DESC
        ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_nifty_data(days: int = 60) -> list:
    """Get recent Nifty 50 data."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM nifty_history 
        ORDER BY date DESC 
        LIMIT ?
    ''', (days,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_sectors_performance() -> list:
    """Get sector-wise average momentum scores."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.sector, 
               AVG(i.momentum_score) as avg_score,
               AVG(i.roc_5) as avg_roc_5,
               COUNT(*) as stock_count
        FROM indicators i
        JOIN stocks s ON i.symbol = s.symbol
        WHERE i.date = (SELECT MAX(date) FROM indicators)
        AND s.sector IS NOT NULL
        GROUP BY s.sector
        ORDER BY avg_score DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()

"""
Yahoo Finance Data Fetcher
Fetches historical OHLCV data for NSE stocks using yfinance library.
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATA_FETCH_DAYS, MIN_DATA_DAYS
from data.stock_list import NIFTY_STOCKS, NIFTY_INDEX, get_stock_sector, STOCK_SECTORS
from data.database import (
    init_db, insert_stock, insert_price_data, insert_nifty_data,
    get_connection
)


def fetch_stock_data(symbol: str, days: int = DATA_FETCH_DAYS) -> pd.DataFrame:
    """
    Fetch historical OHLCV data for a single stock.
    
    Args:
        symbol: Stock symbol with .NS suffix (e.g., 'RELIANCE.NS')
        days: Number of days of history to fetch
        
    Returns:
        DataFrame with OHLCV data, or empty DataFrame if fetch fails
    """
    try:
        ticker = yf.Ticker(symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 30)  # Extra buffer for holidays
        
        df = ticker.history(start=start_date, end=end_date, interval="1d")
        
        if df.empty:
            print(f"  ⚠ No data for {symbol}")
            return pd.DataFrame()
        
        # Clean column names
        df = df.reset_index()
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        # Ensure we have the required columns
        required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            print(f"  ⚠ Missing columns for {symbol}")
            return pd.DataFrame()
        
        # Add adjusted close if not present
        if 'adj_close' not in df.columns:
            df['adj_close'] = df['close']
        
        # Convert date to string format
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        return df[['date', 'open', 'high', 'low', 'close', 'adj_close', 'volume']]
        
    except Exception as e:
        print(f"  ✗ Error fetching {symbol}: {str(e)}")
        return pd.DataFrame()


def fetch_nifty_data(days: int = DATA_FETCH_DAYS) -> pd.DataFrame:
    """Fetch Nifty 50 index data."""
    print(f"Fetching Nifty 50 index data...")
    return fetch_stock_data(NIFTY_INDEX, days)


def get_stock_info(symbol: str) -> dict:
    """Get stock name and other info from Yahoo Finance."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            'name': info.get('longName', info.get('shortName', symbol.replace('.NS', ''))),
            'sector': get_stock_sector(symbol),
            'industry': info.get('industry', None)
        }
    except Exception:
        return {
            'name': symbol.replace('.NS', ''),
            'sector': get_stock_sector(symbol),
            'industry': None
        }


def fetch_all_stocks(progress_callback=None, batch_size: int = 10):
    """
    Fetch data for all stocks in the Nifty list.
    
    Args:
        progress_callback: Optional function to call with progress updates
        batch_size: Number of stocks to fetch before a small delay
    """
    init_db()
    
    total = len(NIFTY_STOCKS)
    successful = 0
    failed = []
    
    print(f"\n{'='*60}")
    print(f"Fetching data for {total} stocks...")
    print(f"{'='*60}\n")
    
    # First fetch Nifty 50 index
    nifty_df = fetch_nifty_data()
    if not nifty_df.empty:
        nifty_data = nifty_df.to_dict('records')
        insert_nifty_data(nifty_data)
        print(f"✓ Nifty 50 index: {len(nifty_data)} days of data\n")
    
    # Fetch individual stocks
    for i, symbol in enumerate(NIFTY_STOCKS, 1):
        try:
            if progress_callback:
                progress_callback(i, total, symbol)
            
            print(f"[{i}/{total}] Fetching {symbol}...", end=" ")
            
            # Get stock info
            info = get_stock_info(symbol)
            insert_stock(symbol, info['name'], info['sector'], info['industry'])
            
            # Get price data
            df = fetch_stock_data(symbol)
            
            if not df.empty and len(df) >= MIN_DATA_DAYS:
                price_data = df.to_dict('records')
                insert_price_data(symbol, price_data)
                print(f"✓ {len(df)} days")
                successful += 1
            elif not df.empty:
                print(f"⚠ Only {len(df)} days (need {MIN_DATA_DAYS})")
                failed.append(symbol)
            else:
                failed.append(symbol)
            
            # Rate limiting - small delay every batch
            if i % batch_size == 0:
                time.sleep(1)
                
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            failed.append(symbol)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Fetch complete: {successful}/{total} stocks successful")
    if failed:
        print(f"Failed stocks ({len(failed)}): {', '.join(failed[:10])}")
        if len(failed) > 10:
            print(f"  ... and {len(failed) - 10} more")
    print(f"{'='*60}\n")
    
    return {
        'total': total,
        'successful': successful,
        'failed': failed
    }


def update_stock_data(symbol: str) -> bool:
    """Update data for a single stock (for daily updates)."""
    try:
        df = fetch_stock_data(symbol, days=5)  # Just get recent days
        if not df.empty:
            price_data = df.to_dict('records')
            insert_price_data(symbol, price_data)
            return True
        return False
    except Exception:
        return False


def update_all_stocks():
    """Update data for all stocks (daily update routine)."""
    print(f"\n{'='*60}")
    print(f"Daily data update started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Update Nifty first
    nifty_df = fetch_stock_data(NIFTY_INDEX, days=5)
    if not nifty_df.empty:
        insert_nifty_data(nifty_df.to_dict('records'))
        print("✓ Nifty 50 index updated")
    
    # Update all stocks
    updated = 0
    for i, symbol in enumerate(NIFTY_STOCKS, 1):
        if update_stock_data(symbol):
            updated += 1
        
        # Rate limiting
        if i % 20 == 0:
            time.sleep(0.5)
            print(f"  Progress: {i}/{len(NIFTY_STOCKS)}")
    
    print(f"\n✓ Updated {updated} stocks")
    return updated


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Stock Data Fetcher')
    parser.add_argument('--full', action='store_true', help='Full fetch of all stocks')
    parser.add_argument('--update', action='store_true', help='Daily update')
    parser.add_argument('--symbol', type=str, help='Fetch single symbol')
    
    args = parser.parse_args()
    
    if args.symbol:
        df = fetch_stock_data(args.symbol)
        print(df)
    elif args.update:
        update_all_stocks()
    else:
        fetch_all_stocks()

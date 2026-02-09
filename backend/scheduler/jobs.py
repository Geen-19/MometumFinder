"""
Scheduler Module
Handles automated daily data updates and analysis.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE, TIMEZONE


def get_scheduler():
    """Get configured scheduler instance."""
    return BackgroundScheduler(timezone=pytz.timezone(TIMEZONE))


def daily_update_job():
    """
    Daily update job - runs after market close.
    
    Tasks:
    1. Fetch latest price data for all stocks
    2. Update Nifty 50 index data
    3. Calculate all technical indicators
    4. Generate momentum scores
    5. Create signal recommendations
    """
    from data.fetcher import update_all_stocks, fetch_nifty_data
    from data.database import insert_nifty_data, get_stock_prices, insert_indicators, insert_signal
    from data.stock_list import NIFTY_STOCKS
    from analysis.indicators import calculate_all_indicators, get_latest_indicators as get_indicator_dict
    from analysis.momentum import calculate_momentum_score
    from analysis.signals import classify_signal
    import pandas as pd
    
    print(f"\n{'='*60}")
    print(f"Daily Update Job Started - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        # Step 1: Update stock data
        print("Step 1: Updating stock price data...")
        update_all_stocks()
        
        # Step 2: Update Nifty data
        print("\nStep 2: Updating Nifty 50 data...")
        nifty_df = fetch_nifty_data(days=5)
        if not nifty_df.empty:
            insert_nifty_data(nifty_df.to_dict('records'))
        
        # Step 3 & 4: Calculate indicators and scores
        print("\nStep 3-4: Calculating indicators and momentum scores...")
        processed = 0
        errors = []
        
        # Get Nifty data for relative strength
        from data.database import get_nifty_data
        nifty_data = get_nifty_data(days=60)
        nifty_df = pd.DataFrame(nifty_data) if nifty_data else pd.DataFrame()
        
        for symbol in NIFTY_STOCKS:
            try:
                # Get price data
                prices = get_stock_prices(symbol, days=60)
                if not prices or len(prices) < 30:
                    continue
                
                # Convert to DataFrame
                df = pd.DataFrame(prices)
                df = df.sort_values('date')
                
                # Calculate indicators
                df_with_indicators = calculate_all_indicators(df, nifty_df)
                
                # Get latest indicators and calculate score
                latest = get_indicator_dict(df_with_indicators)
                latest['momentum_score'] = calculate_momentum_score(latest)
                
                # Save to database
                if latest.get('date'):
                    insert_indicators(symbol, latest['date'], latest)
                    
                    # Generate and save signal
                    signal_type, rationale = classify_signal(latest)
                    insert_signal(
                        symbol, latest['date'], signal_type,
                        latest['momentum_score'], rationale
                    )
                
                processed += 1
                
                if processed % 50 == 0:
                    print(f"  Processed {processed} stocks...")
                    
            except Exception as e:
                errors.append(f"{symbol}: {str(e)}")
        
        print(f"\n✓ Processed {processed} stocks")
        if errors:
            print(f"⚠ {len(errors)} errors occurred")
        
        print(f"\n{'='*60}")
        print(f"Daily Update Job Completed - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n✗ Daily update failed: {str(e)}")
        raise


def setup_scheduler(scheduler: BackgroundScheduler = None) -> BackgroundScheduler:
    """
    Set up the scheduled jobs.
    
    Schedule:
    - Daily at 3:45 PM IST (after market close)
    - Only on weekdays (Monday-Friday)
    """
    if scheduler is None:
        scheduler = get_scheduler()
    
    # Daily job at market close
    scheduler.add_job(
        func=daily_update_job,
        trigger=CronTrigger(
            day_of_week='mon-fri',
            hour=MARKET_CLOSE_HOUR,
            minute=MARKET_CLOSE_MINUTE,
            timezone=pytz.timezone(TIMEZONE)
        ),
        id='daily_update',
        name='Daily Market Update',
        replace_existing=True,
        misfire_grace_time=3600  # Allow 1 hour grace period
    )
    
    print(f"Scheduler configured:")
    print(f"  - Daily update at {MARKET_CLOSE_HOUR}:{MARKET_CLOSE_MINUTE:02d} IST (Mon-Fri)")
    
    return scheduler


def run_manual_update():
    """Run the update job manually (for testing or one-time updates)."""
    print("Starting manual update...")
    daily_update_job()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Scheduler for Stock Analysis')
    parser.add_argument('--run-now', action='store_true', help='Run update immediately')
    parser.add_argument('--start', action='store_true', help='Start scheduler daemon')
    
    args = parser.parse_args()
    
    if args.run_now:
        run_manual_update()
    elif args.start:
        scheduler = setup_scheduler()
        scheduler.start()
        
        print("\nScheduler is running. Press Ctrl+C to stop.")
        
        try:
            # Keep the main thread alive
            import time
            while True:
                time.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            print("\nScheduler stopped.")
    else:
        print("Use --run-now for manual update or --start to run scheduler")

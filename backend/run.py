"""
Stock Analysis Platform - Main Entry Point

Usage:
    python run.py                    # Start API server
    python run.py --fetch-data       # Initial data fetch
    python run.py --update           # Run daily update
    python run.py --scheduler        # Start with scheduler
"""
import argparse
import sys
from pathlib import Path

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent))


def main():
    parser = argparse.ArgumentParser(description='Stock Analysis Platform')
    parser.add_argument('--fetch-data', action='store_true', 
                        help='Fetch initial data for all stocks')
    parser.add_argument('--update', action='store_true',
                        help='Run daily update (fetch + calculate)')
    parser.add_argument('--scheduler', action='store_true',
                        help='Start API with scheduler enabled')
    parser.add_argument('--init-db', action='store_true',
                        help='Initialize database only')
    
    args = parser.parse_args()
    
    if args.init_db:
        from data.database import init_db
        init_db()
        print("Database initialized successfully!")
        return
    
    if args.fetch_data:
        from data.database import init_db
        from data.fetcher import fetch_all_stocks
        
        print("Initializing database...")
        init_db()
        
        print("\nFetching data for all stocks...")
        result = fetch_all_stocks()
        
        print(f"\nFetch complete: {result['successful']}/{result['total']} stocks")
        
        # Run indicator calculation
        print("\nCalculating indicators...")
        from scheduler.jobs import run_manual_update
        run_manual_update()
        
        return
    
    if args.update:
        from scheduler.jobs import run_manual_update
        run_manual_update()
        return
    
    # Default: Start API server
    from data.database import init_db
    init_db()
    
    if args.scheduler:
        from scheduler.jobs import setup_scheduler
        scheduler = setup_scheduler()
        scheduler.start()
        print("Scheduler started!")
    
    from api.app import app
    from config import API_HOST, API_PORT, API_DEBUG
    
    print(f"\nStarting Stock Analysis Platform API...")
    print(f"Server: http://{API_HOST}:{API_PORT}")
    print(f"Endpoints:")
    print(f"  GET  /api/health          - Health check")
    print(f"  GET  /api/screener        - Stock rankings")
    print(f"  GET  /api/stock/<symbol>  - Stock details")
    print(f"  GET  /api/signals         - Signal recommendations")
    print(f"  GET  /api/nifty           - Nifty 50 data")
    print(f"  GET  /api/sectors         - Sector analysis")
    print(f"  GET  /api/top-movers      - Top gainers/losers")
    print(f"  GET  /api/market-overview - Dashboard data")
    print()
    
    app.run(host=API_HOST, port=API_PORT, debug=API_DEBUG)


if __name__ == '__main__':
    main()

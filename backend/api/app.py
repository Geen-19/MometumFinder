"""
Flask REST API for Stock Analysis Platform
Provides endpoints for screener, stock details, signals, and market data.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import pandas as pd
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import API_HOST, API_PORT, API_DEBUG
from data.database import (
    get_all_stocks, get_latest_indicators, get_stock_indicators,
    get_stock_prices, get_latest_signals, get_nifty_data,
    get_sectors_performance, get_connection
)
from data.stock_list import NIFTY_STOCKS, get_stock_sector
from analysis.indicators import calculate_all_indicators, get_latest_indicators as get_indicator_dict
from analysis.momentum import calculate_momentum_score, get_score_breakdown
from analysis.signals import (
    generate_signals, get_signal_summary, get_top_signals,
    analyze_sector_signals, get_market_breadth, SignalType
)


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/screener', methods=['GET'])
def get_screener():
    """
    Get all stocks ranked by momentum score.
    
    Query params:
    - limit: Number of stocks to return (default: 200)
    - sector: Filter by sector
    - min_score: Minimum momentum score
    - signal: Filter by signal type (strong_buy, buy, hold, sell)
    """
    try:
        limit = request.args.get('limit', 200, type=int)
        sector = request.args.get('sector', None)
        min_score = request.args.get('min_score', 0, type=float)
        signal_filter = request.args.get('signal', None)
        
        # Get latest indicators for all stocks
        stocks = get_latest_indicators(limit=500)
        
        if not stocks:
            return jsonify({
                'error': 'No data available. Please run data fetch first.',
                'stocks': []
            }), 200
        
        # Apply filters
        if sector:
            stocks = [s for s in stocks if s.get('sector') == sector]
        
        if min_score > 0:
            stocks = [s for s in stocks if s.get('momentum_score', 0) >= min_score]
        
        # Generate signals for filtering
        signals = generate_signals(stocks)
        
        if signal_filter:
            signal_map = {
                'strong_buy': SignalType.STRONG_BUY,
                'buy': SignalType.BUY,
                'hold': SignalType.HOLD,
                'sell': SignalType.SELL,
                'avoid': SignalType.AVOID
            }
            filter_type = signal_map.get(signal_filter.lower())
            if filter_type:
                signals = [s for s in signals if s.get('signal_type') == filter_type]
        
        # Limit results
        signals = signals[:limit]
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'count': len(signals),
            'stocks': signals
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock_detail(symbol):
    """
    Get detailed analysis for a single stock.
    
    Returns:
    - Current price and indicators
    - Momentum score breakdown
    - Historical indicator data
    - Signal recommendation
    """
    try:
        # Ensure proper symbol format
        if not symbol.endswith('.NS'):
            symbol = f"{symbol}.NS"
        
        # Get price history
        prices = get_stock_prices(symbol, days=60)
        
        if not prices:
            return jsonify({'error': f'No data found for {symbol}'}), 404
        
        # Get indicator history
        indicators = get_stock_indicators(symbol, days=30)
        
        if not indicators:
            return jsonify({'error': f'No indicators calculated for {symbol}'}), 404
        
        # Get latest indicators
        latest = indicators[0] if indicators else {}
        
        # Calculate score breakdown
        breakdown = get_score_breakdown(latest)
        
        # Generate signal
        from analysis.signals import classify_signal
        signal_type, rationale = classify_signal(latest)
        
        # Get stock info
        stocks = get_all_stocks()
        stock_info = next((s for s in stocks if s['symbol'] == symbol), {})
        
        return jsonify({
            'symbol': symbol,
            'name': stock_info.get('name', symbol.replace('.NS', '')),
            'sector': stock_info.get('sector', get_stock_sector(symbol)),
            'current': {
                'price': latest.get('close'),
                'date': latest.get('date'),
                'signal': signal_type,
                'signal_rationale': rationale,
                'momentum_score': latest.get('momentum_score')
            },
            'indicators': {
                'rsi': latest.get('rsi'),
                'roc_5': latest.get('roc_5'),
                'roc_10': latest.get('roc_10'),
                'roc_20': latest.get('roc_20'),
                'atr': latest.get('atr'),
                'sma_20': latest.get('sma_20'),
                'sma_50': latest.get('sma_50'),
                'macd': latest.get('macd'),
                'macd_signal': latest.get('macd_signal'),
                'macd_hist': latest.get('macd_hist'),
                'bb_upper': latest.get('bb_upper'),
                'bb_middle': latest.get('bb_middle'),
                'bb_lower': latest.get('bb_lower'),
                'relative_volume': latest.get('relative_volume'),
                'relative_strength_5': latest.get('relative_strength_5'),
                'relative_strength_10': latest.get('relative_strength_10'),
                'relative_strength_20': latest.get('relative_strength_20')
            },
            'score_breakdown': breakdown,
            'price_history': prices[:30],  # Last 30 days
            'indicator_history': indicators[:30]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/signals', methods=['GET'])
def get_signals_endpoint():
    """
    Get today's signal recommendations.
    
    Query params:
    - type: Filter by signal type (strong_buy, buy, hold, sell, avoid)
    - limit: Number of signals to return (default: 50)
    """
    try:
        signal_type = request.args.get('type', None)
        limit = request.args.get('limit', 50, type=int)
        
        # Get latest indicators
        stocks = get_latest_indicators(limit=500)
        
        if not stocks:
            return jsonify({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'summary': {},
                'signals': [],
                'market_breadth': {}
            })
        
        # Generate signals
        signals = generate_signals(stocks)
        
        # Get summary before filtering
        summary = get_signal_summary(signals)
        breadth = get_market_breadth(signals)
        
        # Apply filter
        if signal_type:
            signal_map = {
                'strong_buy': SignalType.STRONG_BUY,
                'buy': SignalType.BUY,
                'hold': SignalType.HOLD,
                'sell': SignalType.SELL,
                'avoid': SignalType.AVOID
            }
            filter_type = signal_map.get(signal_type.lower())
            if filter_type:
                signals = [s for s in signals if s.get('signal_type') == filter_type]
        
        return jsonify({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'summary': summary,
            'market_breadth': breadth,
            'signals': signals[:limit]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/nifty', methods=['GET'])
def get_nifty_endpoint():
    """
    Get Nifty 50 index data and performance.
    """
    try:
        nifty_data = get_nifty_data(days=60)
        
        if not nifty_data:
            return jsonify({'error': 'No Nifty data available'}), 404
        
        # Get latest and calculate changes
        latest = nifty_data[0] if nifty_data else {}
        prev = nifty_data[1] if len(nifty_data) > 1 else latest
        
        current_close = latest.get('close', 0)
        prev_close = prev.get('close', current_close)
        
        day_change = current_close - prev_close
        day_change_pct = (day_change / prev_close * 100) if prev_close else 0
        
        # Calculate period returns
        week_ago = nifty_data[4] if len(nifty_data) > 4 else latest
        month_ago = nifty_data[19] if len(nifty_data) > 19 else latest
        
        week_return = ((current_close - week_ago.get('close', current_close)) / 
                       week_ago.get('close', current_close) * 100) if week_ago.get('close') else 0
        month_return = ((current_close - month_ago.get('close', current_close)) / 
                        month_ago.get('close', current_close) * 100) if month_ago.get('close') else 0
        
        return jsonify({
            'current_value': current_close,
            'date': latest.get('date'),
            'day_change': round(day_change, 2),
            'day_change_pct': round(day_change_pct, 2),
            'week_return': round(week_return, 2),
            'month_return': round(month_return, 2),
            'history': nifty_data[:30]  # Last 30 days
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sectors', methods=['GET'])
def get_sectors_endpoint():
    """
    Get sector-wise performance and momentum analysis.
    """
    try:
        # Get latest indicators
        stocks = get_latest_indicators(limit=500)
        
        if not stocks:
            return jsonify({'sectors': []})
        
        # Generate signals for sector analysis
        signals = generate_signals(stocks)
        sector_analysis = analyze_sector_signals(signals)
        
        # Convert to list format
        sectors = []
        for sector, data in sector_analysis.items():
            sectors.append({
                'sector': sector,
                'stock_count': data['count'],
                'buy_signals': data['buy_signals'],
                'sell_signals': data['sell_signals'],
                'avg_momentum_score': data['avg_score']
            })
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'sectors': sectors
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/top-movers', methods=['GET'])
def get_top_movers():
    """
    Get top gainers and losers by momentum score change.
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Get latest indicators
        stocks = get_latest_indicators(limit=500)
        
        if not stocks:
            return jsonify({
                'gainers': [],
                'losers': []
            })
        
        # Sort by ROC_5 for recent movers
        gainers = sorted(
            [s for s in stocks if s.get('roc_5') is not None],
            key=lambda x: x.get('roc_5', 0),
            reverse=True
        )[:limit]
        
        losers = sorted(
            [s for s in stocks if s.get('roc_5') is not None],
            key=lambda x: x.get('roc_5', 0)
        )[:limit]
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'gainers': gainers,
            'losers': losers
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['GET'])
def search_stocks():
    """
    Search stocks by symbol or name.
    """
    try:
        query = request.args.get('q', '').upper()
        
        if len(query) < 2:
            return jsonify({'results': []})
        
        stocks = get_all_stocks()
        
        results = [
            s for s in stocks 
            if query in s.get('symbol', '').upper() or 
               query in (s.get('name', '') or '').upper()
        ][:20]
        
        return jsonify({'results': results})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/market-overview', methods=['GET'])
def get_market_overview():
    """
    Get comprehensive market overview for dashboard.
    """
    try:
        # Get Nifty data
        nifty_data = get_nifty_data(days=30)
        nifty_latest = nifty_data[0] if nifty_data else {}
        nifty_prev = nifty_data[1] if len(nifty_data) > 1 else nifty_latest
        
        nifty_change = nifty_latest.get('close', 0) - nifty_prev.get('close', 0)
        nifty_change_pct = (nifty_change / nifty_prev.get('close', 1) * 100) if nifty_prev.get('close') else 0
        
        # Get stock signals
        stocks = get_latest_indicators(limit=500)
        signals = generate_signals(stocks) if stocks else []
        
        summary = get_signal_summary(signals)
        breadth = get_market_breadth(signals)
        
        # Top momentum stocks
        top_momentum = get_top_signals(signals, n=5, signal_types=[SignalType.STRONG_BUY, SignalType.BUY])
        
        # Sector performance
        sector_analysis = analyze_sector_signals(signals) if signals else {}
        top_sectors = list(sector_analysis.items())[:5]
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'nifty': {
                'value': nifty_latest.get('close'),
                'change': round(nifty_change, 2),
                'change_pct': round(nifty_change_pct, 2),
                'date': nifty_latest.get('date')
            },
            'signal_summary': summary,
            'market_breadth': breadth,
            'top_momentum': top_momentum,
            'top_sectors': [
                {'sector': s[0], 'avg_score': s[1]['avg_score'], 'buy_count': s[1]['buy_signals']}
                for s in top_sectors
            ],
            'stock_count': len(stocks) if stocks else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print(f"\n{'='*50}")
    print("Stock Analysis Platform API")
    print(f"Running on http://{API_HOST}:{API_PORT}")
    print(f"{'='*50}\n")
    
    app.run(host=API_HOST, port=API_PORT, debug=API_DEBUG)

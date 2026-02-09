"""
Signal Recommendation Module
Generates trading signal recommendations based on momentum analysis.

Signal categories:
- Strong Buy: Exceptional momentum across all factors
- Buy: Good momentum with confirmation
- Hold: Neutral or mixed signals
- Sell/Avoid: Weak or deteriorating momentum
"""
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import SIGNAL_THRESHOLDS
from analysis.momentum import calculate_momentum_score, get_score_breakdown


class SignalType:
    STRONG_BUY = "Strong Buy"
    BUY = "Buy"
    HOLD = "Hold"
    SELL = "Sell"
    AVOID = "Avoid"


def classify_signal(indicators: Dict) -> tuple:
    """
    Classify a stock into signal category based on its indicators.
    
    Args:
        indicators: Dictionary with all indicator values
        
    Returns:
        Tuple of (signal_type, rationale)
    """
    score = calculate_momentum_score(indicators)
    
    rsi = indicators.get('rsi', 50)
    roc_5 = indicators.get('roc_5', 0) or 0
    roc_10 = indicators.get('roc_10', 0) or 0
    roc_20 = indicators.get('roc_20', 0) or 0
    rs_5 = indicators.get('relative_strength_5', 0) or 0
    rs_10 = indicators.get('relative_strength_10', 0) or 0
    rs_20 = indicators.get('relative_strength_20', 0) or 0
    rel_vol = indicators.get('relative_volume', 1) or 1
    close = indicators.get('close', 0)
    sma_20 = indicators.get('sma_20', 0)
    
    # Build rationale components
    rationale_parts = []
    
    # Check for STRONG BUY conditions
    strong_buy_conditions = [
        score >= SIGNAL_THRESHOLDS['strong_buy_min'],
        all([rs_5 > 0, rs_10 > 0, rs_20 > 0]),
        rel_vol >= SIGNAL_THRESHOLDS['volume_confirmation'],
        sma_20 and close and close > sma_20,
        50 <= rsi <= 65
    ]
    
    if all(strong_buy_conditions):
        rationale_parts.append(f"Momentum score {score:.1f} in top tier")
        rationale_parts.append("Outperforming Nifty across all timeframes")
        rationale_parts.append(f"Strong volume confirmation ({rel_vol:.2f}x)")
        rationale_parts.append("Price above 20-day SMA (uptrend)")
        rationale_parts.append(f"RSI {rsi:.1f} in optimal zone")
        return SignalType.STRONG_BUY, "; ".join(rationale_parts)
    
    # Check for BUY conditions
    buy_conditions = [
        score >= SIGNAL_THRESHOLDS['buy_min'],
        sum([rs_5 > 0, rs_10 > 0, rs_20 > 0]) >= 2,
        rel_vol >= SIGNAL_THRESHOLDS['volume_buy']
    ]
    
    if all(buy_conditions):
        rationale_parts.append(f"Momentum score {score:.1f} shows strength")
        if sum([rs_5 > 0, rs_10 > 0, rs_20 > 0]) == 3:
            rationale_parts.append("Consistent market outperformance")
        else:
            rationale_parts.append("Outperforming Nifty in 2+ timeframes")
        rationale_parts.append(f"Volume {rel_vol:.2f}x average")
        return SignalType.BUY, "; ".join(rationale_parts)
    
    # Check for SELL/AVOID conditions
    if rsi and rsi > SIGNAL_THRESHOLDS['overbought_rsi']:
        return SignalType.SELL, f"RSI {rsi:.1f} indicates overbought conditions - risk of reversal"
    
    if rsi and rsi < SIGNAL_THRESHOLDS['oversold_rsi']:
        return SignalType.AVOID, f"RSI {rsi:.1f} indicates oversold - may continue falling or bounce"
    
    if score < SIGNAL_THRESHOLDS['hold_min']:
        rationale_parts.append(f"Momentum score {score:.1f} below threshold")
        if all([rs_5 < 0, rs_10 < 0, rs_20 < 0]):
            rationale_parts.append("Underperforming Nifty across all timeframes")
            return SignalType.AVOID, "; ".join(rationale_parts)
        else:
            return SignalType.SELL, "; ".join(rationale_parts)
    
    # Default to HOLD
    rationale_parts.append(f"Momentum score {score:.1f} in neutral range")
    if sma_20 and close:
        if close > sma_20:
            rationale_parts.append("Price above 20-day SMA")
        else:
            rationale_parts.append("Price below 20-day SMA")
    
    positive_rs = sum([rs_5 > 0, rs_10 > 0, rs_20 > 0])
    rationale_parts.append(f"Outperforming Nifty in {positive_rs}/3 timeframes")
    
    return SignalType.HOLD, "; ".join(rationale_parts)


def generate_signals(stocks_data: List[Dict]) -> List[Dict]:
    """
    Generate signal recommendations for a list of stocks.
    
    Args:
        stocks_data: List of dictionaries with stock indicators
        
    Returns:
        List of dictionaries with signal information
    """
    signals = []
    
    for stock in stocks_data:
        signal_type, rationale = classify_signal(stock)
        score = calculate_momentum_score(stock)
        
        signals.append({
            'symbol': stock.get('symbol'),
            'name': stock.get('name'),
            'sector': stock.get('sector'),
            'signal_type': signal_type,
            'momentum_score': score,
            'rationale': rationale,
            'close': stock.get('close'),
            'roc_5': stock.get('roc_5'),
            'roc_10': stock.get('roc_10'),
            'rsi': stock.get('rsi'),
            'relative_volume': stock.get('relative_volume'),
            'date': stock.get('date', datetime.now().strftime('%Y-%m-%d'))
        })
    
    # Sort by momentum score (highest first for buys, lowest first for sells)
    signals.sort(key=lambda x: x['momentum_score'], reverse=True)
    
    return signals


def get_signal_summary(signals: List[Dict]) -> Dict:
    """
    Get summary counts of signals by type.
    """
    summary = {
        SignalType.STRONG_BUY: 0,
        SignalType.BUY: 0,
        SignalType.HOLD: 0,
        SignalType.SELL: 0,
        SignalType.AVOID: 0
    }
    
    for signal in signals:
        signal_type = signal.get('signal_type')
        if signal_type in summary:
            summary[signal_type] += 1
    
    return summary


def filter_signals_by_type(signals: List[Dict], 
                           signal_types: List[str]) -> List[Dict]:
    """
    Filter signals to only include specified types.
    """
    return [s for s in signals if s.get('signal_type') in signal_types]


def get_top_signals(signals: List[Dict], n: int = 10, 
                    signal_types: List[str] = None) -> List[Dict]:
    """
    Get top N signals, optionally filtered by type.
    """
    if signal_types:
        signals = filter_signals_by_type(signals, signal_types)
    
    return signals[:n]


def analyze_sector_signals(signals: List[Dict]) -> Dict:
    """
    Analyze signals by sector to identify sector trends.
    """
    sector_data = {}
    
    for signal in signals:
        sector = signal.get('sector', 'Others')
        if sector not in sector_data:
            sector_data[sector] = {
                'count': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'avg_score': 0,
                'total_score': 0
            }
        
        sector_data[sector]['count'] += 1
        sector_data[sector]['total_score'] += signal.get('momentum_score', 0)
        
        if signal.get('signal_type') in [SignalType.STRONG_BUY, SignalType.BUY]:
            sector_data[sector]['buy_signals'] += 1
        elif signal.get('signal_type') in [SignalType.SELL, SignalType.AVOID]:
            sector_data[sector]['sell_signals'] += 1
    
    # Calculate averages
    for sector in sector_data:
        count = sector_data[sector]['count']
        if count > 0:
            sector_data[sector]['avg_score'] = round(
                sector_data[sector]['total_score'] / count, 2
            )
    
    # Sort by average score
    sorted_sectors = sorted(
        sector_data.items(),
        key=lambda x: x[1]['avg_score'],
        reverse=True
    )
    
    return dict(sorted_sectors)


def get_market_breadth(signals: List[Dict]) -> Dict:
    """
    Calculate market breadth indicators.
    
    - Advance/Decline ratio
    - % above key thresholds
    - Average momentum score
    """
    if not signals:
        return {}
    
    total = len(signals)
    advancing = sum(1 for s in signals if s.get('roc_5', 0) and s['roc_5'] > 0)
    declining = total - advancing
    
    above_70 = sum(1 for s in signals if s.get('momentum_score', 0) >= 70)
    above_50 = sum(1 for s in signals if s.get('momentum_score', 0) >= 50)
    below_40 = sum(1 for s in signals if s.get('momentum_score', 0) < 40)
    
    avg_score = sum(s.get('momentum_score', 0) for s in signals) / total
    
    return {
        'total_stocks': total,
        'advancing': advancing,
        'declining': declining,
        'ad_ratio': round(advancing / max(declining, 1), 2),
        'pct_above_70': round(above_70 / total * 100, 1),
        'pct_above_50': round(above_50 / total * 100, 1),
        'pct_below_40': round(below_40 / total * 100, 1),
        'avg_momentum_score': round(avg_score, 2)
    }


if __name__ == "__main__":
    # Test with sample data
    test_stocks = [
        {
            'symbol': 'RELIANCE.NS',
            'name': 'Reliance Industries',
            'sector': 'Oil & Gas',
            'close': 2850.50,
            'roc_5': 3.5,
            'roc_10': 5.2,
            'roc_20': 8.1,
            'rsi': 58.0,
            'relative_volume': 1.55,
            'relative_strength_5': 1.2,
            'relative_strength_10': 2.1,
            'relative_strength_20': 3.5,
            'sma_20': 2750.0
        },
        {
            'symbol': 'TCS.NS',
            'name': 'TCS',
            'sector': 'IT',
            'close': 3450.0,
            'roc_5': -1.2,
            'roc_10': 0.5,
            'roc_20': 2.1,
            'rsi': 45.0,
            'relative_volume': 0.85,
            'relative_strength_5': -0.5,
            'relative_strength_10': 0.2,
            'relative_strength_20': 1.0,
            'sma_20': 3500.0
        }
    ]
    
    signals = generate_signals(test_stocks)
    
    print("Generated Signals:")
    print("=" * 60)
    for sig in signals:
        print(f"\n{sig['symbol']} - {sig['signal_type']}")
        print(f"  Score: {sig['momentum_score']}")
        print(f"  Rationale: {sig['rationale']}")
    
    print("\n" + "=" * 60)
    print("Summary:", get_signal_summary(signals))

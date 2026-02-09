"""
Gems Discovery Module
Identifies undervalued stocks with strong fundamentals that are temporarily oversold.

Gem Criteria:
1. RSI < 35 (oversold)
2. Positive momentum potential (recent decline but not broken trend)
3. Good relative strength vs Nifty on longer timeframe
4. Above-average volume (accumulation signal)
"""
import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import SIGNAL_THRESHOLDS


class GemType:
    DEEP_VALUE = "Deep Value"       # RSI < 25, very oversold
    OVERSOLD_BOUNCE = "Oversold Bounce"  # RSI 25-35, starting to recover
    PULLBACK_BUY = "Pullback Buy"   # RSI 35-45, healthy pullback in uptrend
    VOLUME_SPIKE = "Volume Spike"   # High volume on oversold condition


def identify_gems(stocks_data: List[Dict]) -> List[Dict]:
    """
    Identify gem stocks from the screener data.
    
    A gem is a stock that is:
    1. Temporarily oversold (RSI < 40)
    2. Has shown relative strength on longer timeframes
    3. Has volume confirmation
    4. Price near support levels (Bollinger lower band)
    """
    gems = []
    
    for stock in stocks_data:
        rsi = stock.get('rsi')
        if rsi is None or rsi > 40:
            continue
        
        # Gather indicators
        roc_5 = stock.get('roc_5', 0) or 0
        roc_10 = stock.get('roc_10', 0) or 0
        roc_20 = stock.get('roc_20', 0) or 0
        rel_vol = stock.get('relative_volume', 1) or 1
        rs_5 = stock.get('relative_strength_5', 0) or 0
        rs_10 = stock.get('relative_strength_10', 0) or 0
        rs_20 = stock.get('relative_strength_20', 0) or 0
        close = stock.get('close', 0)
        bb_lower = stock.get('bb_lower', 0)
        bb_middle = stock.get('bb_middle', 0)
        sma_50 = stock.get('sma_50', 0)
        
        # Calculate gem score and type
        gem_score = 0
        gem_type = None
        reasons = []
        
        # RSI scoring (lower = more oversold = higher gem potential)
        if rsi < 25:
            gem_score += 30
            gem_type = GemType.DEEP_VALUE
            reasons.append(f"Deeply oversold RSI ({rsi:.1f})")
        elif rsi < 30:
            gem_score += 25
            gem_type = GemType.OVERSOLD_BOUNCE
            reasons.append(f"Oversold RSI ({rsi:.1f})")
        elif rsi < 35:
            gem_score += 20
            gem_type = GemType.OVERSOLD_BOUNCE
            reasons.append(f"Near oversold RSI ({rsi:.1f})")
        else:
            gem_score += 10
            gem_type = GemType.PULLBACK_BUY
            reasons.append(f"Pullback zone RSI ({rsi:.1f})")
        
        # Price near Bollinger lower band (potential bounce)
        if bb_lower and close and close <= bb_lower * 1.02:
            gem_score += 15
            reasons.append("Price at Bollinger lower band (support)")
        
        # Volume spike on oversold (accumulation)
        if rel_vol >= 1.5:
            gem_score += 15
            gem_type = GemType.VOLUME_SPIKE
            reasons.append(f"High volume ({rel_vol:.1f}x) - potential accumulation")
        elif rel_vol >= 1.2:
            gem_score += 10
            reasons.append(f"Above average volume ({rel_vol:.1f}x)")
        
        # Longer-term relative strength positive (not a falling knife)
        if rs_20 > 0:
            gem_score += 15
            reasons.append("Outperforming Nifty on 20-day basis")
        elif rs_10 > 0:
            gem_score += 10
            reasons.append("Outperforming Nifty on 10-day basis")
        
        # Price recovery signal (short-term ROC improving)
        if roc_5 > roc_10:
            gem_score += 10
            reasons.append("Short-term momentum improving")
        
        # Near SMA50 support
        if sma_50 and close and abs(close - sma_50) / sma_50 < 0.03:
            gem_score += 10
            reasons.append("Price near 50-day SMA support")
        
        # Only include if score is meaningful
        if gem_score >= 30:
            gems.append({
                'symbol': stock.get('symbol'),
                'name': stock.get('name'),
                'sector': stock.get('sector'),
                'gem_type': gem_type,
                'gem_score': gem_score,
                'close': close,
                'rsi': rsi,
                'roc_5': roc_5,
                'roc_20': roc_20,
                'relative_volume': rel_vol,
                'relative_strength_20': rs_20,
                'reasons': reasons,
                'risk_level': get_risk_level(rsi, rel_vol, rs_20),
                'date': stock.get('date', datetime.now().strftime('%Y-%m-%d'))
            })
    
    # Sort by gem score (highest first)
    gems.sort(key=lambda x: x['gem_score'], reverse=True)
    
    return gems


def get_risk_level(rsi: float, rel_vol: float, rs_20: float) -> str:
    """
    Assess risk level for a gem stock.
    """
    risk_score = 0
    
    # Very low RSI is riskier (could be falling knife)
    if rsi < 20:
        risk_score += 3
    elif rsi < 25:
        risk_score += 2
    elif rsi < 30:
        risk_score += 1
    
    # Low volume on oversold is riskier (no accumulation)
    if rel_vol < 0.8:
        risk_score += 2
    elif rel_vol < 1.0:
        risk_score += 1
    
    # Negative relative strength is riskier
    if rs_20 < -5:
        risk_score += 2
    elif rs_20 < 0:
        risk_score += 1
    
    if risk_score >= 5:
        return "High"
    elif risk_score >= 3:
        return "Medium"
    else:
        return "Low"


def get_gem_summary(gems: List[Dict]) -> Dict:
    """
    Get summary statistics for gems.
    """
    if not gems:
        return {
            'total': 0,
            'by_type': {},
            'by_risk': {},
            'avg_rsi': 0,
            'avg_gem_score': 0
        }
    
    by_type = {}
    by_risk = {}
    
    for gem in gems:
        gem_type = gem.get('gem_type', 'Unknown')
        risk = gem.get('risk_level', 'Unknown')
        
        by_type[gem_type] = by_type.get(gem_type, 0) + 1
        by_risk[risk] = by_risk.get(risk, 0) + 1
    
    avg_rsi = sum(g.get('rsi', 30) for g in gems) / len(gems)
    avg_score = sum(g.get('gem_score', 0) for g in gems) / len(gems)
    
    return {
        'total': len(gems),
        'by_type': by_type,
        'by_risk': by_risk,
        'avg_rsi': round(avg_rsi, 1),
        'avg_gem_score': round(avg_score, 1)
    }


def get_sector_gems(gems: List[Dict]) -> Dict:
    """
    Group gems by sector.
    """
    sectors = {}
    
    for gem in gems:
        sector = gem.get('sector', 'Others')
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(gem)
    
    # Sort sectors by count
    return dict(sorted(sectors.items(), key=lambda x: len(x[1]), reverse=True))


if __name__ == "__main__":
    # Test with sample data
    test_stocks = [
        {
            'symbol': 'TEST1.NS',
            'name': 'Test Stock 1',
            'sector': 'IT',
            'close': 100,
            'rsi': 28,
            'roc_5': -3,
            'roc_10': -5,
            'roc_20': -8,
            'relative_volume': 1.8,
            'relative_strength_5': -2,
            'relative_strength_10': -1,
            'relative_strength_20': 3,
            'bb_lower': 98,
            'sma_50': 105
        },
        {
            'symbol': 'TEST2.NS',
            'name': 'Test Stock 2',
            'sector': 'Banking',
            'close': 500,
            'rsi': 22,
            'roc_5': -8,
            'roc_10': -12,
            'roc_20': -15,
            'relative_volume': 2.1,
            'relative_strength_5': -5,
            'relative_strength_10': -3,
            'relative_strength_20': -2,
            'bb_lower': 495,
            'sma_50': 550
        }
    ]
    
    gems = identify_gems(test_stocks)
    
    print("Identified Gems:")
    print("=" * 50)
    for gem in gems:
        print(f"\n{gem['symbol']} - {gem['gem_type']}")
        print(f"  Score: {gem['gem_score']}")
        print(f"  RSI: {gem['rsi']}")
        print(f"  Risk: {gem['risk_level']}")
        print(f"  Reasons: {', '.join(gem['reasons'])}")

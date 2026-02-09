"""
Momentum Scoring Module
Calculates composite momentum scores for stock ranking.

The scoring system combines multiple indicators (SHORT-TERM FOCUS):
- ROC(5): 20% - Short-term momentum (high priority)
- ROC(10): 15% - Medium-term momentum
- ROC(20): 10% - Longer-term trend (reduced)
- Relative Strength: 15% - Market outperformance
- Volume Score: 10% - Confirmation
- RSI Score: 20% - INCREASED for short-term trading
- MA Score: 10% - Moving average crossover signals
"""
import pandas as pd
import numpy as np
from typing import List, Dict
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import SCORE_WEIGHTS


def normalize_to_percentile(values: pd.Series) -> pd.Series:
    """
    Normalize values to 0-100 scale using percentile ranking.
    
    This ensures fair comparison across stocks with different
    volatility characteristics.
    """
    return values.rank(pct=True) * 100


def normalize_minmax(values: pd.Series, inverse: bool = False) -> pd.Series:
    """
    Normalize values to 0-100 scale using min-max normalization.
    
    Args:
        values: Series of values to normalize
        inverse: If True, invert the scale (high values become low scores)
    """
    min_val = values.min()
    max_val = values.max()
    
    if max_val == min_val:
        return pd.Series([50] * len(values), index=values.index)
    
    normalized = (values - min_val) / (max_val - min_val) * 100
    
    if inverse:
        normalized = 100 - normalized
    
    return normalized


def calculate_roc_score(roc_values: pd.Series) -> pd.Series:
    """
    Calculate score for Rate of Change.
    
    Higher ROC = better momentum = higher score
    Using percentile ranking to handle outliers.
    """
    # Handle NaN values
    cleaned = roc_values.fillna(0)
    return normalize_to_percentile(cleaned)


def calculate_volume_score(relative_volume: pd.Series) -> pd.Series:
    """
    Calculate score based on relative volume.
    
    Higher relative volume with positive momentum = confirmation
    - RV > 1.5: Strong confirmation (85-100)
    - RV 1.2-1.5: Good confirmation (70-85)
    - RV 1.0-1.2: Normal (50-70)
    - RV 0.7-1.0: Below average (30-50)
    - RV < 0.7: Weak (0-30)
    """
    def score_volume(rv):
        if pd.isna(rv):
            return 50
        elif rv >= 1.5:
            return 85 + min(15, (rv - 1.5) * 10)
        elif rv >= 1.2:
            return 70 + (rv - 1.2) / 0.3 * 15
        elif rv >= 1.0:
            return 50 + (rv - 1.0) / 0.2 * 20
        elif rv >= 0.7:
            return 30 + (rv - 0.7) / 0.3 * 20
        else:
            return max(0, rv / 0.7 * 30)
    
    return relative_volume.apply(score_volume)


def calculate_rsi_score(rsi_values: pd.Series) -> pd.Series:
    """
    Calculate score based on RSI.
    
    We want RSI in the 'healthy momentum' zone, not extremes.
    - RSI 50-65: Optimal (90-100) - Strong but not overbought
    - RSI 40-50: Good (75-90) - Building momentum
    - RSI 65-75: Caution (60-75) - Getting overbought
    - RSI 30-40: Recovery (50-75) - Bouncing from oversold
    - RSI > 75: Overbought (20-60) - Risk of reversal
    - RSI < 30: Oversold (30-50) - May continue falling
    """
    def score_rsi(rsi):
        if pd.isna(rsi):
            return 50
        elif 50 <= rsi <= 65:
            return 90 + (1 - abs(rsi - 57.5) / 7.5) * 10
        elif 40 <= rsi < 50:
            return 75 + (rsi - 40) / 10 * 15
        elif 65 < rsi <= 75:
            return 60 + (75 - rsi) / 10 * 15
        elif 30 <= rsi < 40:
            return 50 + (rsi - 30) / 10 * 25
        elif rsi > 75:
            return max(20, 60 - (rsi - 75) * 2)
        else:  # rsi < 30
            return max(30, 50 - (30 - rsi) * 2)
    
    return rsi_values.apply(score_rsi)


def calculate_relative_strength_score(rs_5: pd.Series, rs_10: pd.Series, 
                                       rs_20: pd.Series) -> pd.Series:
    """
    Calculate score based on relative strength vs Nifty.
    
    Combines multiple timeframes:
    - All positive: Strong market leader
    - Mixed: Selective momentum
    - All negative: Market laggard
    """
    def score_rs(r5, r10, r20):
        # Handle NaN
        r5 = 0 if pd.isna(r5) else r5
        r10 = 0 if pd.isna(r10) else r10
        r20 = 0 if pd.isna(r20) else r20
        
        # Count positive timeframes
        positive_count = sum([r5 > 0, r10 > 0, r20 > 0])
        
        # Base score from count
        base_score = positive_count * 25  # 0, 25, 50, or 75
        
        # Add magnitude bonus (capped)
        avg_rs = (r5 + r10 + r20) / 3
        magnitude_bonus = min(25, max(-25, avg_rs * 5))
        
        return max(0, min(100, base_score + magnitude_bonus + 25))
    
    scores = []
    for i in range(len(rs_5)):
        scores.append(score_rs(
            rs_5.iloc[i] if isinstance(rs_5, pd.Series) else rs_5,
            rs_10.iloc[i] if isinstance(rs_10, pd.Series) else rs_10,
            rs_20.iloc[i] if isinstance(rs_20, pd.Series) else rs_20
        ))
    
    return pd.Series(scores, index=rs_5.index)


def calculate_momentum_score(indicators: Dict) -> float:
    """
    Calculate final composite momentum score for a single stock.
    
    Args:
        indicators: Dictionary with indicator values
        
    Returns:
        Momentum score from 0-100
    """
    # Get individual scores
    roc_5_score = score_single_roc(indicators.get('roc_5', 0))
    roc_10_score = score_single_roc(indicators.get('roc_10', 0))
    roc_20_score = score_single_roc(indicators.get('roc_20', 0))
    
    volume_score = score_single_volume(indicators.get('relative_volume', 1))
    rsi_score = score_single_rsi(indicators.get('rsi', 50))
    
    rs_score = score_single_rs(
        indicators.get('relative_strength_5', 0),
        indicators.get('relative_strength_10', 0),
        indicators.get('relative_strength_20', 0)
    )
    
    # MA Score - Moving Average analysis
    ma_score = score_single_ma(
        indicators.get('close', 0),
        indicators.get('sma_20', 0),
        indicators.get('sma_50', 0)
    )
    
    # Calculate weighted average
    score = (
        roc_5_score * SCORE_WEIGHTS['roc_5'] +
        roc_10_score * SCORE_WEIGHTS['roc_10'] +
        roc_20_score * SCORE_WEIGHTS['roc_20'] +
        rs_score * SCORE_WEIGHTS['relative_strength'] +
        volume_score * SCORE_WEIGHTS['volume_score'] +
        rsi_score * SCORE_WEIGHTS['rsi_score'] +
        ma_score * SCORE_WEIGHTS.get('ma_score', 0)
    )
    
    return round(score, 2)


def score_single_roc(roc: float) -> float:
    """Score a single ROC value (0-100)."""
    if pd.isna(roc) or roc is None:
        return 50
    
    # Map ROC to score: -20% to +20% range -> 0 to 100
    # Anything beyond gets capped
    score = 50 + (roc / 20) * 50
    return max(0, min(100, score))


def score_single_volume(rv: float) -> float:
    """Score a single relative volume value."""
    if pd.isna(rv) or rv is None:
        return 50
    
    if rv >= 1.5:
        return 85 + min(15, (rv - 1.5) * 10)
    elif rv >= 1.2:
        return 70 + (rv - 1.2) / 0.3 * 15
    elif rv >= 1.0:
        return 50 + (rv - 1.0) / 0.2 * 20
    elif rv >= 0.7:
        return 30 + (rv - 0.7) / 0.3 * 20
    else:
        return max(0, rv / 0.7 * 30)


def score_single_rsi(rsi: float) -> float:
    """Score a single RSI value."""
    if pd.isna(rsi) or rsi is None:
        return 50
    
    if 50 <= rsi <= 65:
        return 90 + (1 - abs(rsi - 57.5) / 7.5) * 10
    elif 40 <= rsi < 50:
        return 75 + (rsi - 40) / 10 * 15
    elif 65 < rsi <= 75:
        return 60 + (75 - rsi) / 10 * 15
    elif 30 <= rsi < 40:
        return 50 + (rsi - 30) / 10 * 25
    elif rsi > 75:
        return max(20, 60 - (rsi - 75) * 2)
    else:
        return max(30, 50 - (30 - rsi) * 2)


def score_single_rs(rs_5: float, rs_10: float, rs_20: float) -> float:
    """Score relative strength across timeframes."""
    rs_5 = 0 if pd.isna(rs_5) or rs_5 is None else rs_5
    rs_10 = 0 if pd.isna(rs_10) or rs_10 is None else rs_10
    rs_20 = 0 if pd.isna(rs_20) or rs_20 is None else rs_20
    
    positive_count = sum([rs_5 > 0, rs_10 > 0, rs_20 > 0])
    base_score = positive_count * 25
    
    avg_rs = (rs_5 + rs_10 + rs_20) / 3
    magnitude_bonus = min(25, max(-25, avg_rs * 5))
    
    return max(0, min(100, base_score + magnitude_bonus + 25))


def score_single_ma(close: float, sma_20: float, sma_50: float) -> float:
    """
    Score based on moving average position and crossovers.
    
    - Price above both SMAs: Strong uptrend (80-100)
    - Price above SMA20, below SMA50: Emerging uptrend (60-80)
    - Price below SMA20, above SMA50: Pullback (40-60)
    - Price below both SMAs: Downtrend (20-40)
    - SMA20 > SMA50: Golden cross bonus
    """
    if pd.isna(close) or close is None or close == 0:
        return 50
    if pd.isna(sma_20) or sma_20 is None or sma_20 == 0:
        return 50
    if pd.isna(sma_50) or sma_50 is None or sma_50 == 0:
        # Only SMA20 available
        if close > sma_20:
            pct_above = ((close - sma_20) / sma_20) * 100
            return min(90, 70 + pct_above * 2)
        else:
            pct_below = ((sma_20 - close) / sma_20) * 100
            return max(20, 50 - pct_below * 2)
    
    score = 50  # Base score
    
    # Price position relative to SMAs
    above_20 = close > sma_20
    above_50 = close > sma_50
    
    if above_20 and above_50:
        # Strong uptrend
        score = 80
        # Bonus for distance above
        pct_above_20 = ((close - sma_20) / sma_20) * 100
        score += min(15, pct_above_20 * 1.5)
    elif above_20 and not above_50:
        # Emerging uptrend / crossing above
        score = 65
        pct_above_20 = ((close - sma_20) / sma_20) * 100
        score += min(10, pct_above_20 * 1.5)
    elif not above_20 and above_50:
        # Pullback in longer uptrend
        score = 45
        pct_below_20 = ((sma_20 - close) / sma_20) * 100
        score -= min(10, pct_below_20)
    else:
        # Downtrend
        score = 30
        pct_below_50 = ((sma_50 - close) / sma_50) * 100
        score -= min(15, pct_below_50)
    
    # Golden cross bonus (SMA20 > SMA50)
    if sma_20 > sma_50:
        score += 5
    else:
        score -= 5
    
    return max(0, min(100, score))

def rank_stocks_by_momentum(stocks_data: List[Dict]) -> List[Dict]:
    """
    Rank a list of stocks by their momentum scores.
    
    Args:
        stocks_data: List of dictionaries with stock indicators
        
    Returns:
        Sorted list with momentum scores and ranks added
    """
    # Calculate scores for all stocks
    for stock in stocks_data:
        stock['momentum_score'] = calculate_momentum_score(stock)
    
    # Sort by score descending
    ranked = sorted(stocks_data, key=lambda x: x['momentum_score'], reverse=True)
    
    # Add ranks
    for i, stock in enumerate(ranked, 1):
        stock['rank'] = i
    
    return ranked


def get_score_breakdown(indicators: Dict) -> Dict:
    """
    Get detailed breakdown of how the momentum score was calculated.
    
    Useful for understanding why a stock has a particular score.
    """
    roc_5_score = score_single_roc(indicators.get('roc_5', 0))
    roc_10_score = score_single_roc(indicators.get('roc_10', 0))
    roc_20_score = score_single_roc(indicators.get('roc_20', 0))
    volume_score = score_single_volume(indicators.get('relative_volume', 1))
    rsi_score = score_single_rsi(indicators.get('rsi', 50))
    rs_score = score_single_rs(
        indicators.get('relative_strength_5', 0),
        indicators.get('relative_strength_10', 0),
        indicators.get('relative_strength_20', 0)
    )
    ma_score = score_single_ma(
        indicators.get('close', 0),
        indicators.get('sma_20', 0),
        indicators.get('sma_50', 0)
    )
    
    return {
        'roc_5': {
            'value': indicators.get('roc_5'),
            'score': round(roc_5_score, 2),
            'weight': SCORE_WEIGHTS['roc_5'],
            'contribution': round(roc_5_score * SCORE_WEIGHTS['roc_5'], 2)
        },
        'roc_10': {
            'value': indicators.get('roc_10'),
            'score': round(roc_10_score, 2),
            'weight': SCORE_WEIGHTS['roc_10'],
            'contribution': round(roc_10_score * SCORE_WEIGHTS['roc_10'], 2)
        },
        'roc_20': {
            'value': indicators.get('roc_20'),
            'score': round(roc_20_score, 2),
            'weight': SCORE_WEIGHTS['roc_20'],
            'contribution': round(roc_20_score * SCORE_WEIGHTS['roc_20'], 2)
        },
        'relative_strength': {
            'value': f"{indicators.get('relative_strength_5', 0):.2f} / {indicators.get('relative_strength_10', 0):.2f} / {indicators.get('relative_strength_20', 0):.2f}",
            'score': round(rs_score, 2),
            'weight': SCORE_WEIGHTS['relative_strength'],
            'contribution': round(rs_score * SCORE_WEIGHTS['relative_strength'], 2)
        },
        'volume': {
            'value': indicators.get('relative_volume'),
            'score': round(volume_score, 2),
            'weight': SCORE_WEIGHTS['volume_score'],
            'contribution': round(volume_score * SCORE_WEIGHTS['volume_score'], 2)
        },
        'rsi': {
            'value': indicators.get('rsi'),
            'score': round(rsi_score, 2),
            'weight': SCORE_WEIGHTS['rsi_score'],
            'contribution': round(rsi_score * SCORE_WEIGHTS['rsi_score'], 2)
        },
        'ma': {
            'value': f"Close: {indicators.get('close', 0):.2f} | SMA20: {indicators.get('sma_20', 0):.2f} | SMA50: {indicators.get('sma_50', 0):.2f}",
            'score': round(ma_score, 2),
            'weight': SCORE_WEIGHTS.get('ma_score', 0),
            'contribution': round(ma_score * SCORE_WEIGHTS.get('ma_score', 0), 2)
        },
        'total_score': calculate_momentum_score(indicators)
    }


if __name__ == "__main__":
    # Test with sample data
    test_indicators = {
        'roc_5': 3.5,
        'roc_10': 5.2,
        'roc_20': 8.1,
        'rsi': 58.0,
        'relative_volume': 1.35,
        'relative_strength_5': 1.2,
        'relative_strength_10': 2.1,
        'relative_strength_20': 3.5
    }
    
    print("Test Momentum Score Calculation")
    print("=" * 50)
    
    breakdown = get_score_breakdown(test_indicators)
    
    for component, data in breakdown.items():
        if component != 'total_score':
            print(f"\n{component}:")
            print(f"  Value: {data['value']}")
            print(f"  Score: {data['score']}/100")
            print(f"  Weight: {data['weight']*100}%")
            print(f"  Contribution: {data['contribution']}")
    
    print(f"\n{'=' * 50}")
    print(f"TOTAL MOMENTUM SCORE: {breakdown['total_score']}/100")

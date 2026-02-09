"""
Technical Indicators Module
Calculates all technical indicators used for momentum analysis.

Indicators implemented:
- RSI (Relative Strength Index)
- ROC (Rate of Change) - 5, 10, 20 day
- ATR (Average True Range)
- SMA (Simple Moving Average) - 20, 50 day
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Volume Analysis
- Relative Strength vs Nifty
"""
import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import INDICATOR_PERIODS


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    RSI measures momentum on a scale of 0-100.
    - RSI > 70: Overbought (potential reversal down)
    - RSI < 30: Oversold (potential reversal up)
    - RSI 40-60: Neutral/healthy momentum
    
    Formula:
    1. Calculate price changes (delta)
    2. Separate gains and losses
    3. Calculate average gain and average loss (EMA)
    4. RS = Average Gain / Average Loss
    5. RSI = 100 - (100 / (1 + RS))
    """
    delta = prices.diff()
    
    gains = delta.copy()
    losses = delta.copy()
    
    gains[gains < 0] = 0
    losses[losses > 0] = 0
    losses = abs(losses)
    
    # Exponential moving average for smoothing
    avg_gain = gains.ewm(span=period, adjust=False).mean()
    avg_loss = losses.ewm(span=period, adjust=False).mean()
    
    # Avoid division by zero
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_roc(prices: pd.Series, period: int) -> pd.Series:
    """
    Calculate Rate of Change (ROC).
    
    ROC measures percentage change over N periods.
    Positive ROC = upward momentum
    Negative ROC = downward momentum
    
    Formula: ((Current Price - Price N days ago) / Price N days ago) * 100
    """
    return ((prices - prices.shift(period)) / prices.shift(period)) * 100


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, 
                  period: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR).
    
    ATR measures volatility in price units.
    Higher ATR = more volatile stock
    Used for stop-loss placement and position sizing.
    
    True Range = max of:
    - High - Low
    - |High - Previous Close|
    - |Low - Previous Close|
    
    ATR = Moving average of True Range
    """
    prev_close = close.shift(1)
    
    tr1 = high - low
    tr2 = abs(high - prev_close)
    tr3 = abs(low - prev_close)
    
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    
    return atr


def calculate_sma(prices: pd.Series, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA).
    
    SMA smooths price data to identify trend direction.
    Price above SMA = bullish tendency
    Price below SMA = bearish tendency
    """
    return prices.rolling(window=period).mean()


def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, 
                   signal: int = 9) -> tuple:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    MACD shows trend direction and strength.
    - MACD Line = 12-day EMA - 26-day EMA
    - Signal Line = 9-day EMA of MACD Line
    - Histogram = MACD Line - Signal Line
    
    Buy signal: MACD crosses above Signal line
    Sell signal: MACD crosses below Signal line
    """
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(prices: pd.Series, period: int = 20, 
                               std_dev: float = 2.0) -> tuple:
    """
    Calculate Bollinger Bands.
    
    Bollinger Bands measure volatility and potential price extremes.
    - Upper Band = SMA + (2 * Standard Deviation)
    - Middle Band = SMA
    - Lower Band = SMA - (2 * Standard Deviation)
    
    Price near upper band = potentially overbought
    Price near lower band = potentially oversold
    """
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    
    return upper_band, sma, lower_band


def calculate_relative_volume(volume: pd.Series, period: int = 20) -> pd.Series:
    """
    Calculate Relative Volume.
    
    Relative Volume = Current Volume / Average Volume
    
    > 1.0 means higher than average volume (more interest)
    > 1.5 means significantly elevated volume (strong signal)
    < 0.7 means low volume (weak signal)
    """
    avg_volume = volume.rolling(window=period).mean()
    return volume / avg_volume.replace(0, np.nan)


def calculate_relative_strength(stock_returns: pd.Series, 
                                 nifty_returns: pd.Series) -> pd.Series:
    """
    Calculate Relative Strength vs Nifty 50.
    
    RS = Stock Return - Nifty Return
    
    Positive RS = Stock outperforming market
    Negative RS = Stock underperforming market
    
    Consistent positive RS = Market leader (good for momentum)
    """
    return stock_returns - nifty_returns


def calculate_all_indicators(df: pd.DataFrame, nifty_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Calculate all technical indicators for a stock.
    
    Args:
        df: DataFrame with columns: date, open, high, low, close, adj_close, volume
        nifty_df: Optional DataFrame with Nifty 50 data for relative strength
        
    Returns:
        DataFrame with all indicators calculated
    """
    # Create a copy to avoid modifying original
    result = df.copy()
    
    # Ensure sorted by date ascending for correct calculations
    result = result.sort_values('date').reset_index(drop=True)
    
    close = result['adj_close'] if 'adj_close' in result.columns else result['close']
    
    # RSI
    result['rsi'] = calculate_rsi(close, INDICATOR_PERIODS['rsi'])
    
    # Rate of Change (multiple timeframes)
    result['roc_5'] = calculate_roc(close, INDICATOR_PERIODS['roc_short'])
    result['roc_10'] = calculate_roc(close, INDICATOR_PERIODS['roc_medium'])
    result['roc_20'] = calculate_roc(close, INDICATOR_PERIODS['roc_long'])
    
    # ATR
    result['atr'] = calculate_atr(
        result['high'], result['low'], close, 
        INDICATOR_PERIODS['atr']
    )
    
    # SMAs
    result['sma_20'] = calculate_sma(close, INDICATOR_PERIODS['sma_short'])
    result['sma_50'] = calculate_sma(close, INDICATOR_PERIODS['sma_long'])
    
    # MACD
    macd, signal, hist = calculate_macd(
        close,
        INDICATOR_PERIODS['macd_fast'],
        INDICATOR_PERIODS['macd_slow'],
        INDICATOR_PERIODS['macd_signal']
    )
    result['macd'] = macd
    result['macd_signal'] = signal
    result['macd_hist'] = hist
    
    # Bollinger Bands
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(
        close,
        INDICATOR_PERIODS['bollinger_period'],
        INDICATOR_PERIODS['bollinger_std']
    )
    result['bb_upper'] = bb_upper
    result['bb_middle'] = bb_middle
    result['bb_lower'] = bb_lower
    
    # Volume Analysis
    result['relative_volume'] = calculate_relative_volume(
        result['volume'], 
        INDICATOR_PERIODS['volume_avg_period']
    )
    
    # Relative Strength vs Nifty (if Nifty data provided)
    if nifty_df is not None and not nifty_df.empty:
        nifty_sorted = nifty_df.sort_values('date').reset_index(drop=True)
        nifty_close = nifty_sorted['close']
        
        # Calculate returns for different periods
        stock_ret_5 = calculate_roc(close, 5)
        stock_ret_10 = calculate_roc(close, 10)
        stock_ret_20 = calculate_roc(close, 20)
        
        nifty_ret_5 = calculate_roc(nifty_close, 5)
        nifty_ret_10 = calculate_roc(nifty_close, 10)
        nifty_ret_20 = calculate_roc(nifty_close, 20)
        
        # Align by date if possible, otherwise use direct comparison
        # Note: This is simplified; in production you'd merge on date
        min_len = min(len(result), len(nifty_sorted))
        
        result['relative_strength_5'] = None
        result['relative_strength_10'] = None
        result['relative_strength_20'] = None
        
        if min_len > 20:
            result.loc[:min_len-1, 'relative_strength_5'] = (
                stock_ret_5.iloc[:min_len].values - nifty_ret_5.iloc[:min_len].values
            )
            result.loc[:min_len-1, 'relative_strength_10'] = (
                stock_ret_10.iloc[:min_len].values - nifty_ret_10.iloc[:min_len].values
            )
            result.loc[:min_len-1, 'relative_strength_20'] = (
                stock_ret_20.iloc[:min_len].values - nifty_ret_20.iloc[:min_len].values
            )
    else:
        result['relative_strength_5'] = None
        result['relative_strength_10'] = None
        result['relative_strength_20'] = None
    
    return result


def get_latest_indicators(df: pd.DataFrame) -> dict:
    """
    Get the most recent indicator values from a DataFrame.
    
    Returns a dictionary with the latest values for all indicators.
    """
    if df.empty:
        return {}
    
    # Get the last row (most recent)
    latest = df.iloc[-1]
    
    return {
        'date': latest.get('date'),
        'close': latest.get('close'),
        'rsi': round(latest.get('rsi', 0), 2) if pd.notna(latest.get('rsi')) else None,
        'roc_5': round(latest.get('roc_5', 0), 2) if pd.notna(latest.get('roc_5')) else None,
        'roc_10': round(latest.get('roc_10', 0), 2) if pd.notna(latest.get('roc_10')) else None,
        'roc_20': round(latest.get('roc_20', 0), 2) if pd.notna(latest.get('roc_20')) else None,
        'atr': round(latest.get('atr', 0), 2) if pd.notna(latest.get('atr')) else None,
        'sma_20': round(latest.get('sma_20', 0), 2) if pd.notna(latest.get('sma_20')) else None,
        'sma_50': round(latest.get('sma_50', 0), 2) if pd.notna(latest.get('sma_50')) else None,
        'macd': round(latest.get('macd', 0), 4) if pd.notna(latest.get('macd')) else None,
        'macd_signal': round(latest.get('macd_signal', 0), 4) if pd.notna(latest.get('macd_signal')) else None,
        'macd_hist': round(latest.get('macd_hist', 0), 4) if pd.notna(latest.get('macd_hist')) else None,
        'bb_upper': round(latest.get('bb_upper', 0), 2) if pd.notna(latest.get('bb_upper')) else None,
        'bb_middle': round(latest.get('bb_middle', 0), 2) if pd.notna(latest.get('bb_middle')) else None,
        'bb_lower': round(latest.get('bb_lower', 0), 2) if pd.notna(latest.get('bb_lower')) else None,
        'relative_volume': round(latest.get('relative_volume', 0), 2) if pd.notna(latest.get('relative_volume')) else None,
        'relative_strength_5': round(latest.get('relative_strength_5', 0), 2) if pd.notna(latest.get('relative_strength_5')) else None,
        'relative_strength_10': round(latest.get('relative_strength_10', 0), 2) if pd.notna(latest.get('relative_strength_10')) else None,
        'relative_strength_20': round(latest.get('relative_strength_20', 0), 2) if pd.notna(latest.get('relative_strength_20')) else None,
    }


if __name__ == "__main__":
    # Test with sample data
    import yfinance as yf
    
    print("Testing indicators with RELIANCE.NS...")
    ticker = yf.Ticker("RELIANCE.NS")
    df = ticker.history(period="3mo")
    df = df.reset_index()
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    if 'adj_close' not in df.columns:
        df['adj_close'] = df['close']
    
    # Calculate indicators
    result = calculate_all_indicators(df)
    
    print("\nLatest indicators:")
    latest = get_latest_indicators(result)
    for key, value in latest.items():
        print(f"  {key}: {value}")

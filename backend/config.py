"""
Stock Analysis Platform - Configuration Settings
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "stock_analyzer.db"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Analysis Parameters
INDICATOR_PERIODS = {
    "rsi": 14,
    "atr": 14,
    "roc_short": 5,
    "roc_medium": 10,
    "roc_long": 20,
    "sma_short": 20,
    "sma_long": 50,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "bollinger_period": 20,
    "bollinger_std": 2,
    "volume_avg_period": 20,
}

# Momentum Score Weights (must sum to 1.0)
# Adjusted for SHORT-TERM investment horizon
SCORE_WEIGHTS = {
    "roc_5": 0.20,      # Short-term momentum (high priority)
    "roc_10": 0.15,     # Medium-term momentum
    "roc_20": 0.10,     # Longer-term trend (reduced)
    "relative_strength": 0.15,  # Market outperformance
    "volume_score": 0.10,       # Confirmation
    "rsi_score": 0.20,          # RSI - INCREASED for short-term
    "ma_score": 0.10,           # Moving Average crossover signals
}

# Signal Thresholds
SIGNAL_THRESHOLDS = {
    "strong_buy_min": 80,
    "buy_min": 70,
    "hold_min": 40,
    "overbought_rsi": 75,
    "oversold_rsi": 25,
    "volume_confirmation": 1.5,
    "volume_buy": 1.2,
}

# Data Fetching
DATA_FETCH_DAYS = 90  # Fetch 90 days of history
MIN_DATA_DAYS = 60    # Minimum days required for analysis

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 5000
API_DEBUG = True

# Scheduler Settings
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 45
TIMEZONE = "Asia/Kolkata"

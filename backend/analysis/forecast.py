"""
Price Forecasting Module
Monte Carlo simulation for price predictions.

Uses historical volatility and drift to simulate possible future price paths.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta


def calculate_monte_carlo_forecast(
    prices: List[Dict],
    days_forward: int = 20,
    num_simulations: int = 1000,
    confidence_levels: List[float] = [0.1, 0.25, 0.5, 0.75, 0.9]
) -> Dict:
    """
    Run Monte Carlo simulation to forecast future prices.
    
    Args:
        prices: List of price dictionaries with 'date' and 'close' keys
        days_forward: Number of days to forecast
        num_simulations: Number of simulation paths
        confidence_levels: Percentiles for confidence bands
        
    Returns:
        Dictionary with forecast data including paths and statistics
    """
    if not prices or len(prices) < 20:
        return {'error': 'Insufficient price data for forecast'}
    
    # Convert to DataFrame and ensure sorted by date
    df = pd.DataFrame(prices)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    close_prices = df['close'].values
    last_price = close_prices[-1]
    
    # Calculate daily returns
    returns = np.diff(np.log(close_prices))
    
    # Calculate drift and volatility
    mu = np.mean(returns)  # Daily drift
    sigma = np.std(returns)  # Daily volatility
    
    # Run simulations
    np.random.seed(42)  # For reproducibility
    simulations = np.zeros((num_simulations, days_forward + 1))
    simulations[:, 0] = last_price
    
    # Generate random walks
    for t in range(1, days_forward + 1):
        random_returns = np.random.normal(mu, sigma, num_simulations)
        simulations[:, t] = simulations[:, t-1] * np.exp(random_returns)
    
    # Calculate statistics at each time step
    forecasts = []
    last_date = df['date'].max()
    
    for t in range(days_forward + 1):
        forecast_date = last_date + timedelta(days=t)
        prices_at_t = simulations[:, t]
        
        percentiles = {
            f'p{int(p*100)}': float(np.percentile(prices_at_t, p*100))
            for p in confidence_levels
        }
        
        forecasts.append({
            'day': t,
            'date': forecast_date.strftime('%Y-%m-%d'),
            'mean': float(np.mean(prices_at_t)),
            'median': float(np.median(prices_at_t)),
            'std': float(np.std(prices_at_t)),
            'min': float(np.min(prices_at_t)),
            'max': float(np.max(prices_at_t)),
            **percentiles
        })
    
    # Calculate expected return and risk metrics
    final_prices = simulations[:, -1]
    expected_return = (np.mean(final_prices) - last_price) / last_price * 100
    prob_profit = np.sum(final_prices > last_price) / num_simulations * 100
    prob_loss_10pct = np.sum(final_prices < last_price * 0.9) / num_simulations * 100
    prob_gain_10pct = np.sum(final_prices > last_price * 1.1) / num_simulations * 100
    
    # Value at Risk (VaR) at 95% confidence
    var_95 = last_price - np.percentile(final_prices, 5)
    var_95_pct = var_95 / last_price * 100
    
    # Sample paths for visualization (take 50 random paths)
    sample_indices = np.random.choice(num_simulations, min(50, num_simulations), replace=False)
    sample_paths = simulations[sample_indices, :].tolist()
    
    return {
        'current_price': float(last_price),
        'forecast_days': days_forward,
        'num_simulations': num_simulations,
        'daily_volatility': float(sigma * 100),  # As percentage
        'annual_volatility': float(sigma * np.sqrt(252) * 100),
        'daily_drift': float(mu * 100),
        'metrics': {
            'expected_return': round(expected_return, 2),
            'prob_profit': round(prob_profit, 1),
            'prob_loss_10pct': round(prob_loss_10pct, 1),
            'prob_gain_10pct': round(prob_gain_10pct, 1),
            'var_95': round(var_95, 2),
            'var_95_pct': round(var_95_pct, 2),
            'target_low': round(np.percentile(final_prices, 10), 2),
            'target_mid': round(np.percentile(final_prices, 50), 2),
            'target_high': round(np.percentile(final_prices, 90), 2),
        },
        'forecast': forecasts,
        'sample_paths': sample_paths
    }


def calculate_trend_forecast(prices: List[Dict], days_forward: int = 20) -> Dict:
    """
    Simple trend-based forecast using linear regression.
    Useful as a baseline comparison to Monte Carlo.
    """
    if not prices or len(prices) < 10:
        return {'error': 'Insufficient data'}
    
    df = pd.DataFrame(prices)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Use last 30 days for trend
    recent = df.tail(30).copy()
    recent['x'] = range(len(recent))
    
    # Linear regression
    x = recent['x'].values
    y = recent['close'].values
    
    n = len(x)
    slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)
    intercept = (np.sum(y) - slope * np.sum(x)) / n
    
    # Calculate R-squared
    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    # Project forward
    last_x = x[-1]
    last_date = pd.to_datetime(df['date'].max())
    
    projections = []
    for t in range(days_forward + 1):
        proj_x = last_x + t + 1
        proj_price = slope * proj_x + intercept
        proj_date = last_date + timedelta(days=t)
        projections.append({
            'day': t,
            'date': proj_date.strftime('%Y-%m-%d'),
            'price': round(max(0, proj_price), 2)
        })
    
    trend = 'Uptrend' if slope > 0 else 'Downtrend' if slope < 0 else 'Sideways'
    daily_change = slope / y[-1] * 100 if y[-1] > 0 else 0
    
    return {
        'trend': trend,
        'slope': round(slope, 4),
        'daily_change_pct': round(daily_change, 2),
        'r_squared': round(r_squared, 3),
        'confidence': 'High' if r_squared > 0.8 else 'Medium' if r_squared > 0.5 else 'Low',
        'projections': projections
    }


def get_volatility_analysis(prices: List[Dict]) -> Dict:
    """
    Analyze historical volatility patterns.
    """
    if not prices or len(prices) < 20:
        return {'error': 'Insufficient data'}
    
    df = pd.DataFrame(prices)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    close = df['close'].values
    returns = np.diff(np.log(close)) * 100  # Percentage returns
    
    # Rolling volatility (10-day)
    rolling_vol = []
    for i in range(10, len(returns) + 1):
        window = returns[i-10:i]
        rolling_vol.append({
            'date': df['date'].iloc[i].strftime('%Y-%m-%d'),
            'volatility': round(np.std(window) * np.sqrt(252), 2)
        })
    
    current_vol = np.std(returns[-10:]) * np.sqrt(252) if len(returns) >= 10 else 0
    avg_vol = np.std(returns) * np.sqrt(252)
    
    vol_regime = 'High' if current_vol > avg_vol * 1.2 else 'Low' if current_vol < avg_vol * 0.8 else 'Normal'
    
    return {
        'current_volatility': round(current_vol, 2),
        'average_volatility': round(avg_vol, 2),
        'volatility_regime': vol_regime,
        'max_daily_gain': round(max(returns), 2) if len(returns) > 0 else 0,
        'max_daily_loss': round(min(returns), 2) if len(returns) > 0 else 0,
        'positive_days_pct': round(np.sum(returns > 0) / len(returns) * 100, 1) if len(returns) > 0 else 50,
        'rolling_volatility': rolling_vol[-20:] if len(rolling_vol) > 20 else rolling_vol
    }


if __name__ == "__main__":
    # Test with sample data
    import random
    
    # Generate sample price data
    base_price = 100
    prices = []
    current_price = base_price
    
    for i in range(60):
        current_price *= (1 + random.gauss(0.001, 0.02))
        prices.append({
            'date': (datetime.now() - timedelta(days=60-i)).strftime('%Y-%m-%d'),
            'close': current_price
        })
    
    forecast = calculate_monte_carlo_forecast(prices, days_forward=20)
    
    print("Monte Carlo Forecast Results")
    print("=" * 50)
    print(f"Current Price: ₹{forecast['current_price']:.2f}")
    print(f"Daily Volatility: {forecast['daily_volatility']:.2f}%")
    print(f"Expected Return (20d): {forecast['metrics']['expected_return']:.1f}%")
    print(f"Probability of Profit: {forecast['metrics']['prob_profit']:.1f}%")
    print(f"\nPrice Targets:")
    print(f"  Low (10%): ₹{forecast['metrics']['target_low']:.2f}")
    print(f"  Mid (50%): ₹{forecast['metrics']['target_mid']:.2f}")
    print(f"  High (90%): ₹{forecast['metrics']['target_high']:.2f}")

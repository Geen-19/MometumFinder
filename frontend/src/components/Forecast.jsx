import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
    AreaChart, Area, LineChart, Line, XAxis, YAxis, Tooltip,
    ResponsiveContainer, ReferenceLine, ComposedChart
} from 'recharts';
import api, { formatPrice, formatPercent } from '../services/api';

const Forecast = () => {
    const { symbol } = useParams();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [forecastDays, setForecastDays] = useState(20);

    useEffect(() => {
        fetchForecast();
    }, [symbol, forecastDays]);

    const fetchForecast = async () => {
        try {
            setLoading(true);
            const response = await api.get(`/api/forecast/${symbol}`, {
                params: { days: forecastDays }
            });
            setData(response.data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const getProbabilityColor = (prob) => {
        if (prob >= 60) return 'text-emerald-400';
        if (prob >= 40) return 'text-amber-400';
        return 'text-red-400';
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-primary"></div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="text-center py-12">
                <p className="text-red-400">{error || 'Failed to load forecast'}</p>
                <Link to={`/stock/${symbol}`} className="text-accent-primary mt-4 inline-block">
                    ← Back to Stock Details
                </Link>
            </div>
        );
    }

    const { forecast, volatility } = data;
    const metrics = forecast?.metrics || {};
    const forecasts = forecast?.forecast || [];

    // Prepare chart data
    const chartData = forecasts.map(f => ({
        day: f.day,
        date: f.date,
        mean: f.mean,
        p10: f.p10,
        p25: f.p25,
        p50: f.p50,
        p75: f.p75,
        p90: f.p90,
        min: f.min,
        max: f.max
    }));

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <Link
                        to={`/stock/${symbol}`}
                        className="text-gray-400 hover:text-white text-sm flex items-center gap-1 mb-2"
                    >
                        ← Back to {symbol}
                    </Link>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                        <span className="text-2xl">📈</span> Price Forecast
                    </h1>
                    <p className="text-gray-400 text-sm mt-1">
                        Monte Carlo simulation with {forecast?.num_simulations?.toLocaleString()} paths
                    </p>
                </div>
                <div className="flex gap-2">
                    {[10, 20, 30, 60].map(days => (
                        <button
                            key={days}
                            onClick={() => setForecastDays(days)}
                            className={`px-3 py-2 rounded-lg text-sm transition-colors ${forecastDays === days
                                    ? 'bg-accent-primary text-white'
                                    : 'bg-dark-card border border-dark-border text-gray-400 hover:text-white'
                                }`}
                        >
                            {days}D
                        </button>
                    ))}
                </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-dark-card border border-dark-border rounded-xl p-4">
                    <div className="text-gray-400 text-sm">Current Price</div>
                    <div className="text-2xl font-bold text-white">
                        {formatPrice(forecast?.current_price)}
                    </div>
                </div>
                <div className="bg-dark-card border border-dark-border rounded-xl p-4">
                    <div className="text-gray-400 text-sm">Expected Return</div>
                    <div className={`text-2xl font-bold ${metrics.expected_return >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {metrics.expected_return >= 0 ? '+' : ''}{metrics.expected_return?.toFixed(1)}%
                    </div>
                </div>
                <div className="bg-dark-card border border-dark-border rounded-xl p-4">
                    <div className="text-gray-400 text-sm">Prob. of Profit</div>
                    <div className={`text-2xl font-bold ${getProbabilityColor(metrics.prob_profit)}`}>
                        {metrics.prob_profit?.toFixed(0)}%
                    </div>
                </div>
                <div className="bg-dark-card border border-dark-border rounded-xl p-4">
                    <div className="text-gray-400 text-sm">Annual Volatility</div>
                    <div className="text-2xl font-bold text-amber-400">
                        {forecast?.annual_volatility?.toFixed(1)}%
                    </div>
                </div>
            </div>

            {/* Forecast Chart */}
            <div className="bg-dark-card border border-dark-border rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">
                    Price Forecast (with Confidence Bands)
                </h3>
                <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={chartData}>
                            <defs>
                                <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.3} />
                                    <stop offset="100%" stopColor="#06b6d4" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <XAxis
                                dataKey="date"
                                stroke="#6b7280"
                                tick={{ fontSize: 10 }}
                                tickFormatter={(val) => val.slice(5)}
                            />
                            <YAxis
                                stroke="#6b7280"
                                tick={{ fontSize: 10 }}
                                domain={['auto', 'auto']}
                                tickFormatter={(val) => `₹${val.toFixed(0)}`}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1a1a2e',
                                    border: '1px solid #374151',
                                    borderRadius: '8px'
                                }}
                                formatter={(value, name) => {
                                    const labels = {
                                        p90: '90th %ile',
                                        p75: '75th %ile',
                                        p50: 'Median',
                                        p25: '25th %ile',
                                        p10: '10th %ile',
                                        mean: 'Mean'
                                    };
                                    return [formatPrice(value), labels[name] || name];
                                }}
                            />
                            <ReferenceLine
                                y={forecast?.current_price}
                                stroke="#6b7280"
                                strokeDasharray="5 5"
                                label={{ value: 'Current', position: 'right', fill: '#6b7280', fontSize: 10 }}
                            />

                            {/* Confidence bands */}
                            <Area
                                type="monotone"
                                dataKey="p90"
                                stroke="none"
                                fill="#22c55e"
                                fillOpacity={0.1}
                            />
                            <Area
                                type="monotone"
                                dataKey="p10"
                                stroke="none"
                                fill="#1a1a2e"
                                fillOpacity={1}
                            />
                            <Area
                                type="monotone"
                                dataKey="p75"
                                stroke="none"
                                fill="#22c55e"
                                fillOpacity={0.15}
                            />
                            <Area
                                type="monotone"
                                dataKey="p25"
                                stroke="none"
                                fill="#1a1a2e"
                                fillOpacity={1}
                            />

                            {/* Key lines */}
                            <Line
                                type="monotone"
                                dataKey="p50"
                                stroke="#06b6d4"
                                strokeWidth={2}
                                dot={false}
                                name="Median"
                            />
                            <Line
                                type="monotone"
                                dataKey="mean"
                                stroke="#f59e0b"
                                strokeWidth={1.5}
                                strokeDasharray="5 5"
                                dot={false}
                                name="Mean"
                            />
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>
                <div className="flex justify-center gap-6 mt-4 text-xs">
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-0.5 bg-cyan-500"></div>
                        <span className="text-gray-400">Median (50th)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-0.5 bg-amber-500 border-dashed"></div>
                        <span className="text-gray-400">Mean</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-3 bg-emerald-500/20 rounded"></div>
                        <span className="text-gray-400">25-75th %ile</span>
                    </div>
                </div>
            </div>

            {/* Price Targets & Risk */}
            <div className="grid md:grid-cols-2 gap-6">
                {/* Price Targets */}
                <div className="bg-dark-card border border-dark-border rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">
                        {forecastDays}-Day Price Targets
                    </h3>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center p-3 bg-emerald-500/10 rounded-lg">
                            <span className="text-emerald-400">Bullish (90th %ile)</span>
                            <span className="text-white font-semibold">{formatPrice(metrics.target_high)}</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-blue-500/10 rounded-lg">
                            <span className="text-blue-400">Base Case (Median)</span>
                            <span className="text-white font-semibold">{formatPrice(metrics.target_mid)}</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-red-500/10 rounded-lg">
                            <span className="text-red-400">Bearish (10th %ile)</span>
                            <span className="text-white font-semibold">{formatPrice(metrics.target_low)}</span>
                        </div>
                    </div>
                </div>

                {/* Risk Metrics */}
                <div className="bg-dark-card border border-dark-border rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Risk Analysis</h3>
                    <div className="space-y-4">
                        <div>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-gray-400">Prob. of 10%+ Gain</span>
                                <span className="text-emerald-400">{metrics.prob_gain_10pct?.toFixed(0)}%</span>
                            </div>
                            <div className="h-2 bg-dark-lighter rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-emerald-500 rounded-full"
                                    style={{ width: `${metrics.prob_gain_10pct}%` }}
                                />
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-gray-400">Prob. of 10%+ Loss</span>
                                <span className="text-red-400">{metrics.prob_loss_10pct?.toFixed(0)}%</span>
                            </div>
                            <div className="h-2 bg-dark-lighter rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-red-500 rounded-full"
                                    style={{ width: `${metrics.prob_loss_10pct}%` }}
                                />
                            </div>
                        </div>
                        <div className="pt-4 border-t border-dark-border">
                            <div className="flex justify-between">
                                <span className="text-gray-400">Value at Risk (95%)</span>
                                <span className="text-amber-400">
                                    {formatPrice(metrics.var_95)} ({metrics.var_95_pct?.toFixed(1)}%)
                                </span>
                            </div>
                            <p className="text-gray-500 text-xs mt-1">
                                With 95% confidence, you won't lose more than this amount
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Volatility Analysis */}
            {volatility && !volatility.error && (
                <div className="bg-dark-card border border-dark-border rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Volatility Analysis</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                            <div className="text-gray-400 text-sm">Current Vol</div>
                            <div className="text-xl font-semibold text-white">
                                {volatility.current_volatility?.toFixed(1)}%
                            </div>
                        </div>
                        <div>
                            <div className="text-gray-400 text-sm">Avg Vol</div>
                            <div className="text-xl font-semibold text-white">
                                {volatility.average_volatility?.toFixed(1)}%
                            </div>
                        </div>
                        <div>
                            <div className="text-gray-400 text-sm">Regime</div>
                            <div className={`text-xl font-semibold ${volatility.volatility_regime === 'High' ? 'text-red-400' :
                                    volatility.volatility_regime === 'Low' ? 'text-emerald-400' : 'text-amber-400'
                                }`}>
                                {volatility.volatility_regime}
                            </div>
                        </div>
                        <div>
                            <div className="text-gray-400 text-sm">% Positive Days</div>
                            <div className="text-xl font-semibold text-white">
                                {volatility.positive_days_pct?.toFixed(0)}%
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Disclaimer */}
            <div className="bg-amber-900/20 border border-amber-500/20 rounded-xl p-4 text-sm text-amber-400/80">
                <strong>⚠️ Disclaimer:</strong> This forecast is based on Monte Carlo simulation using historical
                volatility. Past performance does not guarantee future results. Use this as one of many tools
                in your analysis, not as sole investment advice.
            </div>
        </div>
    );
};

export default Forecast;

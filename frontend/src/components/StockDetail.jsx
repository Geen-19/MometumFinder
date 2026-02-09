import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Area, ComposedChart } from 'recharts'
import api, { formatNumber, formatPercent, getSignalColor, getScoreColor } from '../services/api'

function StockDetail() {
    const { symbol } = useParams()
    const navigate = useNavigate()
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (symbol) {
            fetchStockData()
        }
    }, [symbol])

    const fetchStockData = async () => {
        try {
            setLoading(true)
            setError(null)
            const result = await api.getStockDetail(symbol)
            setData(result)
        } catch (err) {
            setError('Failed to load stock data')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="space-y-6">
                <div className="h-8 w-48 skeleton"></div>
                <div className="card h-96 skeleton"></div>
            </div>
        )
    }

    if (error || !data) {
        return (
            <div className="card text-center py-12">
                <p className="text-5xl mb-4">📊</p>
                <h2 className="text-xl font-semibold text-dark-100 mb-2">Stock Not Found</h2>
                <p className="text-dark-400 mb-6">{error || `No data available for ${symbol}`}</p>
                <button onClick={() => navigate('/screener')} className="btn-primary">
                    Back to Screener
                </button>
            </div>
        )
    }

    const priceHistory = data.price_history ? [...data.price_history].reverse() : []

    return (
        <div className="space-y-6 animate-in">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div>
                    <button
                        onClick={() => navigate(-1)}
                        className="text-dark-400 hover:text-dark-200 text-sm mb-2 flex items-center gap-1"
                    >
                        ← Back
                    </button>
                    <h1 className="text-3xl font-bold text-dark-50">
                        {data.symbol?.replace('.NS', '')}
                    </h1>
                    <p className="text-dark-400 mt-1">{data.name}</p>
                    <p className="text-sm text-dark-500">{data.sector}</p>
                </div>
                <div className="text-right">
                    <p className="text-3xl font-bold text-dark-50">
                        ₹{formatNumber(data.current?.price, 2)}
                    </p>
                    <span className={`badge text-base mt-2 ${getSignalColor(data.current?.signal)}`}>
                        {data.current?.signal}
                    </span>
                </div>
            </div>

            {/* Momentum Score Card */}
            <div className="card">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-dark-50">Momentum Score</h2>
                    <span className="text-4xl font-bold text-primary-400">
                        {formatNumber(data.current?.momentum_score, 0)}
                    </span>
                </div>

                {/* Score Gauge */}
                <div className="h-4 bg-dark-700 rounded-full overflow-hidden mb-4">
                    <div
                        className={`h-full bg-gradient-to-r ${getScoreColor(data.current?.momentum_score)} transition-all duration-500`}
                        style={{ width: `${Math.min(100, data.current?.momentum_score || 0)}%` }}
                    ></div>
                </div>

                {/* Score Breakdown */}
                {data.score_breakdown && (
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-6">
                        {Object.entries(data.score_breakdown).filter(([key]) => key !== 'total_score').map(([key, item]) => (
                            <ScoreBreakdownItem key={key} name={key} data={item} />
                        ))}
                    </div>
                )}

                {/* Signal Rationale */}
                <div className="mt-6 pt-6 border-t border-dark-700/50">
                    <p className="text-sm text-dark-400 mb-2">Analysis</p>
                    <p className="text-dark-200">{data.current?.signal_rationale}</p>
                </div>
            </div>

            {/* Price Chart */}
            <div className="card">
                <h2 className="card-header">Price History (30 Days)</h2>
                <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={priceHistory}>
                            <defs>
                                <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis
                                dataKey="date"
                                stroke="#64748b"
                                fontSize={12}
                                tickFormatter={(date) => new Date(date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                            />
                            <YAxis
                                stroke="#64748b"
                                fontSize={12}
                                domain={['auto', 'auto']}
                                tickFormatter={(val) => `₹${val.toLocaleString()}`}
                            />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                labelStyle={{ color: '#f8fafc' }}
                                formatter={(value, name) => [`₹${Number(value).toLocaleString()}`, name === 'close' ? 'Close' : name]}
                                labelFormatter={(date) => new Date(date).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })}
                            />
                            {data.indicators?.sma_20 && (
                                <ReferenceLine y={data.indicators.sma_20} stroke="#f59e0b" strokeDasharray="5 5" label="" />
                            )}
                            <Area
                                type="monotone"
                                dataKey="close"
                                stroke="#6366f1"
                                strokeWidth={2}
                                fill="url(#priceGradient)"
                            />
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>

                {/* Price Levels */}
                {data.indicators && (
                    <div className="grid grid-cols-3 sm:grid-cols-6 gap-4 mt-6 pt-6 border-t border-dark-700/50">
                        <PriceLevel label="Current" value={data.current?.price} />
                        <PriceLevel label="SMA 20" value={data.indicators.sma_20} />
                        <PriceLevel label="SMA 50" value={data.indicators.sma_50} />
                        <PriceLevel label="BB Upper" value={data.indicators.bb_upper} />
                        <PriceLevel label="BB Middle" value={data.indicators.bb_middle} />
                        <PriceLevel label="BB Lower" value={data.indicators.bb_lower} />
                    </div>
                )}
            </div>

            {/* Technical Indicators */}
            <div className="card">
                <h2 className="card-header">Technical Indicators</h2>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
                    <IndicatorItem
                        label="RSI (14)"
                        value={data.indicators?.rsi}
                        status={getRsiStatus(data.indicators?.rsi)}
                    />
                    <IndicatorItem
                        label="ROC (5d)"
                        value={data.indicators?.roc_5}
                        suffix="%"
                        colored
                    />
                    <IndicatorItem
                        label="ROC (10d)"
                        value={data.indicators?.roc_10}
                        suffix="%"
                        colored
                    />
                    <IndicatorItem
                        label="ROC (20d)"
                        value={data.indicators?.roc_20}
                        suffix="%"
                        colored
                    />
                    <IndicatorItem
                        label="ATR (14)"
                        value={data.indicators?.atr}
                    />
                    <IndicatorItem
                        label="Rel. Volume"
                        value={data.indicators?.relative_volume}
                        suffix="x"
                    />
                    <IndicatorItem
                        label="MACD"
                        value={data.indicators?.macd}
                    />
                    <IndicatorItem
                        label="MACD Signal"
                        value={data.indicators?.macd_signal}
                    />
                </div>

                {/* Relative Strength */}
                <div className="mt-6 pt-6 border-t border-dark-700/50">
                    <h3 className="text-sm font-medium text-dark-300 mb-4">Relative Strength vs Nifty 50</h3>
                    <div className="grid grid-cols-3 gap-4">
                        <RSItem label="5 Day" value={data.indicators?.relative_strength_5} />
                        <RSItem label="10 Day" value={data.indicators?.relative_strength_10} />
                        <RSItem label="20 Day" value={data.indicators?.relative_strength_20} />
                    </div>
                </div>
            </div>
        </div>
    )
}

function ScoreBreakdownItem({ name, data }) {
    const displayName = {
        'roc_5': 'ROC (5d)',
        'roc_10': 'ROC (10d)',
        'roc_20': 'ROC (20d)',
        'relative_strength': 'Rel. Strength',
        'volume': 'Volume',
        'rsi': 'RSI',
    }[name] || name

    return (
        <div className="bg-dark-800/50 rounded-lg p-3">
            <div className="flex justify-between items-start mb-2">
                <span className="text-xs text-dark-400">{displayName}</span>
                <span className="text-xs text-dark-500">{(data.weight * 100)}%</span>
            </div>
            <p className="text-lg font-semibold text-dark-100">{formatNumber(data.score, 0)}</p>
            <div className="h-1.5 bg-dark-700 rounded-full mt-2 overflow-hidden">
                <div
                    className={`h-full bg-gradient-to-r ${getScoreColor(data.score)}`}
                    style={{ width: `${data.score}%` }}
                ></div>
            </div>
            <p className="text-xs text-dark-500 mt-1">+{formatNumber(data.contribution, 1)} pts</p>
        </div>
    )
}

function PriceLevel({ label, value }) {
    return (
        <div>
            <p className="text-xs text-dark-500">{label}</p>
            <p className="font-mono text-dark-200">₹{formatNumber(value, 2)}</p>
        </div>
    )
}

function IndicatorItem({ label, value, suffix = '', status, colored = false }) {
    let textColor = 'text-dark-100'
    if (colored && value !== null && value !== undefined) {
        textColor = value >= 0 ? 'text-positive' : 'text-negative'
    }

    return (
        <div>
            <p className="text-xs text-dark-500 mb-1">{label}</p>
            <p className={`text-xl font-mono ${textColor}`}>
                {formatNumber(value, 2)}{suffix}
            </p>
            {status && <p className={`text-xs ${status.color}`}>{status.text}</p>}
        </div>
    )
}

function RSItem({ label, value }) {
    const isPositive = (value || 0) >= 0
    return (
        <div className={`p-3 rounded-lg text-center ${isPositive ? 'bg-success-500/10' : 'bg-danger-500/10'}`}>
            <p className="text-xs text-dark-400">{label}</p>
            <p className={`text-xl font-mono ${isPositive ? 'text-positive' : 'text-negative'}`}>
                {formatPercent(value)}
            </p>
            <p className="text-xs text-dark-500">{isPositive ? 'Outperforming' : 'Underperforming'}</p>
        </div>
    )
}

function getRsiStatus(rsi) {
    if (!rsi) return null
    if (rsi > 70) return { text: 'Overbought', color: 'text-danger-400' }
    if (rsi < 30) return { text: 'Oversold', color: 'text-success-400' }
    if (rsi >= 50 && rsi <= 65) return { text: 'Optimal', color: 'text-primary-400' }
    return { text: 'Neutral', color: 'text-dark-400' }
}

export default StockDetail

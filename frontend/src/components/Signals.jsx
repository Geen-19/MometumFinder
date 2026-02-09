import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api, { formatNumber, formatPercent, getSignalColor } from '../services/api'

function Signals() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState('')

    useEffect(() => {
        fetchSignals()
    }, [])

    const fetchSignals = async () => {
        try {
            setLoading(true)
            const result = await api.getSignals({ limit: 100 })
            setData(result)
        } catch (err) {
            console.error('Failed to fetch signals:', err)
        } finally {
            setLoading(false)
        }
    }

    const filteredSignals = filter
        ? data?.signals?.filter(s => s.signal_type === filter)
        : data?.signals

    if (loading) {
        return (
            <div className="space-y-6">
                <div className="h-8 w-48 skeleton"></div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[1, 2, 3, 4].map(i => (
                        <div key={i} className="card h-40 skeleton"></div>
                    ))}
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6 animate-in">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-dark-50">Signal Recommendations</h1>
                    <p className="text-dark-400 mt-1">
                        Generated on {data?.date || new Date().toLocaleDateString('en-IN')}
                    </p>
                </div>
                <button onClick={fetchSignals} className="btn-secondary flex items-center gap-2">
                    <span>🔄</span> Refresh
                </button>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                {[
                    { type: 'Strong Buy', icon: '🚀' },
                    { type: 'Buy', icon: '📈' },
                    { type: 'Hold', icon: '⏸️' },
                    { type: 'Sell', icon: '📉' },
                    { type: 'Avoid', icon: '⚠️' },
                ].map(({ type, icon }) => (
                    <button
                        key={type}
                        onClick={() => setFilter(filter === type ? '' : type)}
                        className={`card p-4 text-center transition-all ${filter === type ? 'ring-2 ring-primary-500' : ''
                            } ${getSignalColor(type)}`}
                    >
                        <div className="text-2xl mb-2">{icon}</div>
                        <p className="text-2xl font-bold">{data?.summary?.[type] || 0}</p>
                        <p className="text-xs mt-1">{type}</p>
                    </button>
                ))}
            </div>

            {/* Market Breadth */}
            <div className="card">
                <h2 className="card-header">Market Breadth</h2>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <BreadthItem
                        label="Advancing"
                        value={data?.market_breadth?.advancing}
                        color="text-positive"
                    />
                    <BreadthItem
                        label="Declining"
                        value={data?.market_breadth?.declining}
                        color="text-negative"
                    />
                    <BreadthItem
                        label="A/D Ratio"
                        value={data?.market_breadth?.ad_ratio}
                    />
                    <BreadthItem
                        label="Above 70 Score"
                        value={`${data?.market_breadth?.pct_above_70 || 0}%`}
                    />
                </div>
            </div>

            {/* Filter Indicator */}
            {filter && (
                <div className="flex items-center gap-2">
                    <span className="text-dark-400">Filtered by:</span>
                    <span className={`badge ${getSignalColor(filter)}`}>{filter}</span>
                    <button
                        onClick={() => setFilter('')}
                        className="text-dark-400 hover:text-dark-200"
                    >
                        ✕
                    </button>
                </div>
            )}

            {/* Signal Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredSignals?.map((signal) => (
                    <SignalCard key={signal.symbol} signal={signal} />
                ))}
            </div>

            {(!filteredSignals || filteredSignals.length === 0) && (
                <div className="card text-center py-12">
                    <p className="text-dark-400">No signals found</p>
                </div>
            )}
        </div>
    )
}

function BreadthItem({ label, value, color = 'text-dark-100' }) {
    return (
        <div className="text-center">
            <p className={`text-2xl font-bold ${color}`}>{value ?? '-'}</p>
            <p className="text-xs text-dark-400">{label}</p>
        </div>
    )
}

function SignalCard({ signal }) {
    return (
        <Link
            to={`/stock/${signal.symbol}`}
            className="card hover:border-primary-500/50 transition-all group"
        >
            <div className="flex items-start justify-between">
                <div>
                    <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-dark-50 group-hover:text-primary-400 transition-colors">
                            {signal.symbol?.replace('.NS', '')}
                        </h3>
                        <span className={`badge ${getSignalColor(signal.signal_type)}`}>
                            {signal.signal_type}
                        </span>
                    </div>
                    <p className="text-sm text-dark-400 mt-1">{signal.sector}</p>
                </div>
                <div className="text-right">
                    <p className="text-2xl font-bold text-primary-400">
                        {formatNumber(signal.momentum_score, 0)}
                    </p>
                    <p className="text-xs text-dark-500">Momentum Score</p>
                </div>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-dark-700/50">
                <div>
                    <p className="text-xs text-dark-500">Price</p>
                    <p className="font-mono text-dark-200">₹{formatNumber(signal.close, 2)}</p>
                </div>
                <div>
                    <p className="text-xs text-dark-500">ROC (5d)</p>
                    <p className={`font-mono ${(signal.roc_5 || 0) >= 0 ? 'text-positive' : 'text-negative'}`}>
                        {formatPercent(signal.roc_5)}
                    </p>
                </div>
                <div>
                    <p className="text-xs text-dark-500">RSI</p>
                    <p className="font-mono text-dark-200">{formatNumber(signal.rsi, 1)}</p>
                </div>
            </div>

            {/* Rationale */}
            <div className="mt-4 pt-4 border-t border-dark-700/50">
                <p className="text-xs text-dark-500 mb-1">Analysis</p>
                <p className="text-sm text-dark-300 line-clamp-2">{signal.rationale}</p>
            </div>
        </Link>
    )
}

export default Signals

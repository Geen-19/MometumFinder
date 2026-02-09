import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import api, { formatNumber, formatPercent, getSignalColor, getScoreColor } from '../services/api'

function Dashboard() {
    const [data, setData] = useState(null)
    const [niftyData, setNiftyData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            setLoading(true)
            const [overview, nifty] = await Promise.all([
                api.getMarketOverview(),
                api.getNifty()
            ])
            setData(overview)
            setNiftyData(nifty)
        } catch (err) {
            setError('Failed to load data. Make sure the backend is running.')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return <LoadingState />
    }

    if (error) {
        return <ErrorState message={error} onRetry={fetchData} />
    }

    return (
        <div className="space-y-6 animate-in">
            {/* Page Title */}
            <div>
                <h1 className="text-2xl font-bold text-dark-50">Dashboard</h1>
                <p className="text-dark-400 mt-1">Market overview and top momentum stocks</p>
            </div>

            {/* Nifty & Market Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard
                    title="Nifty 50"
                    value={formatNumber(data?.nifty?.value, 2)}
                    change={data?.nifty?.change_pct}
                    icon="📈"
                />
                <MetricCard
                    title="Stocks Analyzed"
                    value={data?.stock_count || 0}
                    subtitle="Nifty 500"
                    icon="📊"
                />
                <MetricCard
                    title="Avg Momentum"
                    value={formatNumber(data?.market_breadth?.avg_momentum_score, 1)}
                    subtitle="Market average"
                    icon="⚡"
                />
                <MetricCard
                    title="Advance/Decline"
                    value={`${data?.market_breadth?.advancing || 0}/${data?.market_breadth?.declining || 0}`}
                    subtitle={`Ratio: ${data?.market_breadth?.ad_ratio || 0}`}
                    icon="📉"
                />
            </div>

            {/* Signal Summary */}
            <div className="card">
                <h2 className="card-header">Signal Summary</h2>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
                    <SignalBadge type="Strong Buy" count={data?.signal_summary?.['Strong Buy'] || 0} />
                    <SignalBadge type="Buy" count={data?.signal_summary?.['Buy'] || 0} />
                    <SignalBadge type="Hold" count={data?.signal_summary?.['Hold'] || 0} />
                    <SignalBadge type="Sell" count={data?.signal_summary?.['Sell'] || 0} />
                    <SignalBadge type="Avoid" count={data?.signal_summary?.['Avoid'] || 0} />
                </div>
            </div>

            {/* Charts and Lists */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Nifty Chart */}
                <div className="card">
                    <h2 className="card-header">Nifty 50 Performance</h2>
                    {niftyData?.history && (
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={[...niftyData.history].reverse()}>
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
                                        tickFormatter={(val) => val.toLocaleString()}
                                    />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                        labelStyle={{ color: '#f8fafc' }}
                                        formatter={(value) => [value.toLocaleString(), 'Nifty 50']}
                                        labelFormatter={(date) => new Date(date).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="close"
                                        stroke="#6366f1"
                                        strokeWidth={2}
                                        dot={false}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    )}
                    <div className="mt-4 flex gap-4 text-sm">
                        <div>
                            <span className="text-dark-400">1 Week: </span>
                            <span className={niftyData?.week_return >= 0 ? 'text-positive' : 'text-negative'}>
                                {formatPercent(niftyData?.week_return)}
                            </span>
                        </div>
                        <div>
                            <span className="text-dark-400">1 Month: </span>
                            <span className={niftyData?.month_return >= 0 ? 'text-positive' : 'text-negative'}>
                                {formatPercent(niftyData?.month_return)}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Top Momentum Stocks */}
                <div className="card">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-semibold text-dark-50">Top Momentum Stocks</h2>
                        <Link to="/screener" className="text-primary-400 hover:text-primary-300 text-sm">
                            View All →
                        </Link>
                    </div>
                    <div className="space-y-3">
                        {data?.top_momentum?.map((stock, index) => (
                            <Link
                                key={stock.symbol}
                                to={`/stock/${stock.symbol}`}
                                className="flex items-center gap-4 p-3 rounded-lg bg-dark-800/50 hover:bg-dark-800 transition-colors"
                            >
                                <span className="w-6 h-6 flex items-center justify-center rounded-full bg-primary-600/20 text-primary-400 text-xs font-medium">
                                    {index + 1}
                                </span>
                                <div className="flex-1 min-w-0">
                                    <p className="font-medium text-dark-100 truncate">{stock.symbol?.replace('.NS', '')}</p>
                                    <p className="text-xs text-dark-400">{stock.sector}</p>
                                </div>
                                <div className="text-right">
                                    <p className="font-mono text-sm text-dark-100">{formatNumber(stock.momentum_score, 1)}</p>
                                    <span className={`text-xs px-2 py-0.5 rounded-full ${getSignalColor(stock.signal_type)}`}>
                                        {stock.signal_type}
                                    </span>
                                </div>
                            </Link>
                        ))}
                        {(!data?.top_momentum || data.top_momentum.length === 0) && (
                            <p className="text-dark-400 text-center py-4">No data available</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Top Sectors */}
            <div className="card">
                <h2 className="card-header">Top Performing Sectors</h2>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                    {data?.top_sectors?.map((sector) => (
                        <div key={sector.sector} className="p-4 rounded-lg bg-dark-800/50">
                            <p className="font-medium text-dark-100 truncate">{sector.sector}</p>
                            <p className="text-2xl font-bold text-primary-400 mt-1">{formatNumber(sector.avg_score, 1)}</p>
                            <p className="text-xs text-dark-400 mt-1">{sector.buy_count} buy signals</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

// Sub-components
function MetricCard({ title, value, change, subtitle, icon }) {
    return (
        <div className="card flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-primary-600/20 flex items-center justify-center text-2xl">
                {icon}
            </div>
            <div>
                <p className="text-sm text-dark-400">{title}</p>
                <p className="text-2xl font-bold text-dark-50">{value}</p>
                {change !== undefined && (
                    <p className={`text-sm ${change >= 0 ? 'text-positive' : 'text-negative'}`}>
                        {formatPercent(change)}
                    </p>
                )}
                {subtitle && <p className="text-xs text-dark-500">{subtitle}</p>}
            </div>
        </div>
    )
}

function SignalBadge({ type, count }) {
    return (
        <div className={`p-4 rounded-lg text-center ${getSignalColor(type)}`}>
            <p className="text-2xl font-bold">{count}</p>
            <p className="text-xs mt-1">{type}</p>
        </div>
    )
}

function LoadingState() {
    return (
        <div className="space-y-6">
            <div className="h-8 w-48 skeleton"></div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map(i => (
                    <div key={i} className="card h-24 skeleton"></div>
                ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="card h-80 skeleton"></div>
                <div className="card h-80 skeleton"></div>
            </div>
        </div>
    )
}

function ErrorState({ message, onRetry }) {
    return (
        <div className="card text-center py-12">
            <div className="text-5xl mb-4">⚠️</div>
            <h2 className="text-xl font-semibold text-dark-100 mb-2">Unable to Load Data</h2>
            <p className="text-dark-400 mb-6">{message}</p>
            <button onClick={onRetry} className="btn-primary">
                Try Again
            </button>
        </div>
    )
}

export default Dashboard

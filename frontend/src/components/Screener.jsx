import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import api, { formatNumber, formatPercent, getSignalColor, getScoreColor } from '../services/api'

function Screener() {
    const [stocks, setStocks] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [searchTerm, setSearchTerm] = useState('')
    const [sectorFilter, setSectorFilter] = useState('')
    const [signalFilter, setSignalFilter] = useState('')
    const [sortConfig, setSortConfig] = useState({ key: 'momentum_score', direction: 'desc' })

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            setLoading(true)
            const data = await api.getScreener({ limit: 500 })
            setStocks(data.stocks || [])
        } catch (err) {
            setError('Failed to load screener data')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    // Get unique sectors for filter
    const sectors = useMemo(() => {
        const uniqueSectors = [...new Set(stocks.map(s => s.sector).filter(Boolean))]
        return uniqueSectors.sort()
    }, [stocks])

    // Filter and sort stocks
    const filteredStocks = useMemo(() => {
        let result = [...stocks]

        // Search filter
        if (searchTerm) {
            const term = searchTerm.toLowerCase()
            result = result.filter(s =>
                s.symbol?.toLowerCase().includes(term) ||
                s.name?.toLowerCase().includes(term)
            )
        }

        // Sector filter
        if (sectorFilter) {
            result = result.filter(s => s.sector === sectorFilter)
        }

        // Signal filter
        if (signalFilter) {
            result = result.filter(s => s.signal_type === signalFilter)
        }

        // Sort
        result.sort((a, b) => {
            const aVal = a[sortConfig.key] ?? 0
            const bVal = b[sortConfig.key] ?? 0

            if (sortConfig.direction === 'asc') {
                return aVal > bVal ? 1 : -1
            }
            return aVal < bVal ? 1 : -1
        })

        return result
    }, [stocks, searchTerm, sectorFilter, signalFilter, sortConfig])

    const handleSort = (key) => {
        setSortConfig(prev => ({
            key,
            direction: prev.key === key && prev.direction === 'desc' ? 'asc' : 'desc'
        }))
    }

    const SortIcon = ({ columnKey }) => {
        if (sortConfig.key !== columnKey) return <span className="text-dark-600">↕</span>
        return <span className="text-primary-400">{sortConfig.direction === 'desc' ? '↓' : '↑'}</span>
    }

    if (loading) {
        return (
            <div className="space-y-6">
                <div className="h-8 w-48 skeleton"></div>
                <div className="card h-96 skeleton"></div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="card text-center py-12">
                <p className="text-dark-400">{error}</p>
                <button onClick={fetchData} className="btn-primary mt-4">Retry</button>
            </div>
        )
    }

    return (
        <div className="space-y-6 animate-in">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-dark-50">Stock Screener</h1>
                    <p className="text-dark-400 mt-1">
                        {filteredStocks.length} of {stocks.length} stocks
                    </p>
                </div>
                <button onClick={fetchData} className="btn-secondary flex items-center gap-2">
                    <span>🔄</span> Refresh
                </button>
            </div>

            {/* Filters */}
            <div className="card">
                <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                    {/* Search */}
                    <div>
                        <label className="text-xs text-dark-400 mb-1 block">Search</label>
                        <input
                            type="text"
                            placeholder="Symbol or name..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="input w-full"
                        />
                    </div>

                    {/* Sector Filter */}
                    <div>
                        <label className="text-xs text-dark-400 mb-1 block">Sector</label>
                        <select
                            value={sectorFilter}
                            onChange={(e) => setSectorFilter(e.target.value)}
                            className="input w-full"
                        >
                            <option value="">All Sectors</option>
                            {sectors.map(sector => (
                                <option key={sector} value={sector}>{sector}</option>
                            ))}
                        </select>
                    </div>

                    {/* Signal Filter */}
                    <div>
                        <label className="text-xs text-dark-400 mb-1 block">Signal</label>
                        <select
                            value={signalFilter}
                            onChange={(e) => setSignalFilter(e.target.value)}
                            className="input w-full"
                        >
                            <option value="">All Signals</option>
                            <option value="Strong Buy">Strong Buy</option>
                            <option value="Buy">Buy</option>
                            <option value="Hold">Hold</option>
                            <option value="Sell">Sell</option>
                            <option value="Avoid">Avoid</option>
                        </select>
                    </div>

                    {/* Clear Filters */}
                    <div className="flex items-end">
                        <button
                            onClick={() => {
                                setSearchTerm('')
                                setSectorFilter('')
                                setSignalFilter('')
                            }}
                            className="btn-secondary w-full"
                        >
                            Clear Filters
                        </button>
                    </div>
                </div>
            </div>

            {/* Table */}
            <div className="card overflow-hidden p-0">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-dark-800/50">
                            <tr>
                                <th className="px-4 py-3 text-left table-header">#</th>
                                <th className="px-4 py-3 text-left table-header">Symbol</th>
                                <th className="px-4 py-3 text-left table-header hidden sm:table-cell">Sector</th>
                                <th
                                    className="px-4 py-3 text-right table-header cursor-pointer hover:text-dark-200"
                                    onClick={() => handleSort('close')}
                                >
                                    Price <SortIcon columnKey="close" />
                                </th>
                                <th
                                    className="px-4 py-3 text-right table-header cursor-pointer hover:text-dark-200"
                                    onClick={() => handleSort('momentum_score')}
                                >
                                    Score <SortIcon columnKey="momentum_score" />
                                </th>
                                <th
                                    className="px-4 py-3 text-right table-header cursor-pointer hover:text-dark-200 hidden md:table-cell"
                                    onClick={() => handleSort('roc_5')}
                                >
                                    ROC(5d) <SortIcon columnKey="roc_5" />
                                </th>
                                <th
                                    className="px-4 py-3 text-right table-header cursor-pointer hover:text-dark-200 hidden lg:table-cell"
                                    onClick={() => handleSort('rsi')}
                                >
                                    RSI <SortIcon columnKey="rsi" />
                                </th>
                                <th className="px-4 py-3 text-center table-header">Signal</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-dark-700/50">
                            {filteredStocks.map((stock, index) => (
                                <tr
                                    key={stock.symbol}
                                    className="hover:bg-dark-800/30 transition-colors"
                                >
                                    <td className="px-4 py-3 text-dark-500 text-sm">{index + 1}</td>
                                    <td className="px-4 py-3">
                                        <Link
                                            to={`/stock/${stock.symbol}`}
                                            className="hover:text-primary-400 transition-colors"
                                        >
                                            <p className="font-medium text-dark-100">
                                                {stock.symbol?.replace('.NS', '')}
                                            </p>
                                            <p className="text-xs text-dark-500 truncate max-w-[150px]">
                                                {stock.name}
                                            </p>
                                        </Link>
                                    </td>
                                    <td className="px-4 py-3 text-dark-400 text-sm hidden sm:table-cell">
                                        {stock.sector || '-'}
                                    </td>
                                    <td className="px-4 py-3 text-right font-mono text-dark-200">
                                        ₹{formatNumber(stock.close, 2)}
                                    </td>
                                    <td className="px-4 py-3 text-right">
                                        <div className="flex items-center justify-end gap-2">
                                            <div className="w-16 h-2 bg-dark-700 rounded-full overflow-hidden hidden sm:block">
                                                <div
                                                    className={`h-full bg-gradient-to-r ${getScoreColor(stock.momentum_score)}`}
                                                    style={{ width: `${Math.min(100, stock.momentum_score || 0)}%` }}
                                                ></div>
                                            </div>
                                            <span className="font-mono font-medium text-dark-100 w-10">
                                                {formatNumber(stock.momentum_score, 0)}
                                            </span>
                                        </div>
                                    </td>
                                    <td className={`px-4 py-3 text-right font-mono hidden md:table-cell ${(stock.roc_5 || 0) >= 0 ? 'text-positive' : 'text-negative'
                                        }`}>
                                        {formatPercent(stock.roc_5)}
                                    </td>
                                    <td className="px-4 py-3 text-right font-mono text-dark-300 hidden lg:table-cell">
                                        {formatNumber(stock.rsi, 1)}
                                    </td>
                                    <td className="px-4 py-3 text-center">
                                        <span className={`badge ${getSignalColor(stock.signal_type)}`}>
                                            {stock.signal_type}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {filteredStocks.length === 0 && (
                    <div className="text-center py-12 text-dark-400">
                        No stocks found matching your criteria
                    </div>
                )}
            </div>
        </div>
    )
}

export default Screener

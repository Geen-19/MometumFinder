import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api, { formatPrice, formatPercent, getSignalColor } from '../services/api';

const Gems = () => {
    const [gems, setGems] = useState([]);
    const [summary, setSummary] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [riskFilter, setRiskFilter] = useState('');
    const [sectorFilter, setSectorFilter] = useState('');
    const [sectors, setSectors] = useState([]);

    useEffect(() => {
        fetchGems();
    }, [riskFilter, sectorFilter]);

    const fetchGems = async () => {
        try {
            setLoading(true);
            const params = {};
            if (riskFilter) params.risk = riskFilter;
            if (sectorFilter) params.sector = sectorFilter;

            const response = await api.get('/api/gems', { params });
            setGems(response.data.gems || []);
            setSummary(response.data.summary || {});

            // Extract unique sectors
            if (response.data.sector_breakdown) {
                setSectors(Object.keys(response.data.sector_breakdown));
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const getGemTypeColor = (type) => {
        switch (type) {
            case 'Deep Value': return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
            case 'Oversold Bounce': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
            case 'Pullback Buy': return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30';
            case 'Volume Spike': return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
            default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
        }
    };

    const getRiskColor = (risk) => {
        switch (risk) {
            case 'Low': return 'text-emerald-400';
            case 'Medium': return 'text-amber-400';
            case 'High': return 'text-red-400';
            default: return 'text-gray-400';
        }
    };

    const getRsiGradient = (rsi) => {
        // Lower RSI = more oversold = more attractive
        if (rsi < 25) return 'from-purple-600 to-purple-400';
        if (rsi < 30) return 'from-blue-600 to-blue-400';
        if (rsi < 35) return 'from-cyan-600 to-cyan-400';
        return 'from-gray-600 to-gray-400';
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-primary"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-12">
                <p className="text-red-400">{error}</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                        <span className="text-2xl">💎</span> Gems Discovery
                    </h1>
                    <p className="text-gray-400 text-sm mt-1">
                        Oversold stocks with bounce potential - high reward opportunities
                    </p>
                </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-dark-card border border-dark-border rounded-xl p-4">
                    <div className="text-3xl font-bold text-white">{summary.total || 0}</div>
                    <div className="text-gray-400 text-sm">Total Gems</div>
                </div>
                <div className="bg-dark-card border border-dark-border rounded-xl p-4">
                    <div className="text-3xl font-bold text-purple-400">
                        {summary.by_type?.['Deep Value'] || 0}
                    </div>
                    <div className="text-gray-400 text-sm">Deep Value</div>
                </div>
                <div className="bg-dark-card border border-dark-border rounded-xl p-4">
                    <div className="text-3xl font-bold text-blue-400">
                        {summary.by_type?.['Oversold Bounce'] || 0}
                    </div>
                    <div className="text-gray-400 text-sm">Oversold Bounce</div>
                </div>
                <div className="bg-dark-card border border-dark-border rounded-xl p-4">
                    <div className="text-3xl font-bold text-accent-primary">
                        {summary.avg_rsi?.toFixed(1) || '-'}
                    </div>
                    <div className="text-gray-400 text-sm">Avg RSI</div>
                </div>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-4 bg-dark-card border border-dark-border rounded-xl p-4">
                <div className="flex-1 min-w-[200px]">
                    <label className="text-xs text-gray-400 block mb-1">Risk Level</label>
                    <select
                        value={riskFilter}
                        onChange={(e) => setRiskFilter(e.target.value)}
                        className="w-full bg-dark-lighter border border-dark-border rounded-lg px-3 py-2 text-white"
                    >
                        <option value="">All Risk Levels</option>
                        <option value="low">Low Risk</option>
                        <option value="medium">Medium Risk</option>
                        <option value="high">High Risk</option>
                    </select>
                </div>
                <div className="flex-1 min-w-[200px]">
                    <label className="text-xs text-gray-400 block mb-1">Sector</label>
                    <select
                        value={sectorFilter}
                        onChange={(e) => setSectorFilter(e.target.value)}
                        className="w-full bg-dark-lighter border border-dark-border rounded-lg px-3 py-2 text-white"
                    >
                        <option value="">All Sectors</option>
                        {sectors.map(sector => (
                            <option key={sector} value={sector}>{sector}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Gems Grid */}
            {gems.length === 0 ? (
                <div className="text-center py-12 bg-dark-card border border-dark-border rounded-xl">
                    <div className="text-4xl mb-4">🔍</div>
                    <p className="text-gray-400">No gems found with current filters</p>
                    <p className="text-gray-500 text-sm mt-2">
                        Gems appear when stocks become oversold (RSI &lt; 40)
                    </p>
                </div>
            ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {gems.map((gem) => (
                        <Link
                            key={gem.symbol}
                            to={`/stock/${gem.symbol.replace('.NS', '')}`}
                            className="group bg-dark-card border border-dark-border rounded-xl p-5 hover:border-accent-primary/50 transition-all"
                        >
                            {/* Header */}
                            <div className="flex items-start justify-between mb-4">
                                <div>
                                    <h3 className="text-lg font-semibold text-white group-hover:text-accent-primary transition-colors">
                                        {gem.symbol.replace('.NS', '')}
                                    </h3>
                                    <p className="text-gray-400 text-sm">{gem.sector}</p>
                                </div>
                                <div className={`px-2 py-1 rounded-lg border text-xs font-medium ${getGemTypeColor(gem.gem_type)}`}>
                                    {gem.gem_type}
                                </div>
                            </div>

                            {/* RSI Gauge */}
                            <div className="mb-4">
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-gray-400">RSI</span>
                                    <span className={`font-semibold ${gem.rsi < 30 ? 'text-purple-400' : 'text-blue-400'}`}>
                                        {gem.rsi?.toFixed(1)}
                                    </span>
                                </div>
                                <div className="h-2 bg-dark-lighter rounded-full overflow-hidden">
                                    <div
                                        className={`h-full bg-gradient-to-r ${getRsiGradient(gem.rsi)} rounded-full transition-all`}
                                        style={{ width: `${gem.rsi}%` }}
                                    />
                                </div>
                                <div className="flex justify-between text-xs text-gray-500 mt-1">
                                    <span>Oversold</span>
                                    <span>30</span>
                                    <span>70</span>
                                </div>
                            </div>

                            {/* Stats */}
                            <div className="grid grid-cols-2 gap-3 mb-4">
                                <div className="bg-dark-lighter rounded-lg p-2">
                                    <div className="text-gray-400 text-xs">Price</div>
                                    <div className="text-white font-medium">{formatPrice(gem.close)}</div>
                                </div>
                                <div className="bg-dark-lighter rounded-lg p-2">
                                    <div className="text-gray-400 text-xs">Volume</div>
                                    <div className={`font-medium ${gem.relative_volume >= 1.5 ? 'text-amber-400' : 'text-white'}`}>
                                        {gem.relative_volume?.toFixed(1)}x
                                    </div>
                                </div>
                                <div className="bg-dark-lighter rounded-lg p-2">
                                    <div className="text-gray-400 text-xs">Gem Score</div>
                                    <div className="text-accent-primary font-medium">{gem.gem_score}</div>
                                </div>
                                <div className="bg-dark-lighter rounded-lg p-2">
                                    <div className="text-gray-400 text-xs">Risk</div>
                                    <div className={`font-medium ${getRiskColor(gem.risk_level)}`}>
                                        {gem.risk_level}
                                    </div>
                                </div>
                            </div>

                            {/* Reasons */}
                            <div className="space-y-1">
                                {gem.reasons?.slice(0, 3).map((reason, i) => (
                                    <div key={i} className="flex items-center gap-2 text-xs">
                                        <span className="text-emerald-400">✓</span>
                                        <span className="text-gray-400">{reason}</span>
                                    </div>
                                ))}
                            </div>
                        </Link>
                    ))}
                </div>
            )}

            {/* Educational Note */}
            <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-purple-500/20 rounded-xl p-5">
                <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
                    <span>📚</span> About Gems
                </h3>
                <div className="text-gray-400 text-sm space-y-2">
                    <p>
                        <strong className="text-purple-400">Deep Value:</strong> RSI below 25 - Extremely oversold, highest reward but higher risk
                    </p>
                    <p>
                        <strong className="text-blue-400">Oversold Bounce:</strong> RSI 25-35 - Good bounce potential with moderate risk
                    </p>
                    <p>
                        <strong className="text-cyan-400">Pullback Buy:</strong> RSI 35-45 - Healthy pullback in uptrend
                    </p>
                    <p>
                        <strong className="text-amber-400">Volume Spike:</strong> High volume on oversold - Potential accumulation by institutions
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Gems;

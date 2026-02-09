import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import Screener from './components/Screener'
import StockDetail from './components/StockDetail'
import Signals from './components/Signals'

function App() {
    const [currentTime, setCurrentTime] = useState(new Date())

    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 60000)
        return () => clearInterval(timer)
    }, [])

    const navItems = [
        { path: '/', label: 'Dashboard', icon: '📊' },
        { path: '/screener', label: 'Screener', icon: '🔍' },
        { path: '/signals', label: 'Signals', icon: '📡' },
    ]

    return (
        <Router>
            <div className="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950">
                {/* Header */}
                <header className="sticky top-0 z-50 bg-dark-900/80 backdrop-blur-xl border-b border-dark-700/50">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div className="flex items-center justify-between h-16">
                            {/* Logo */}
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center">
                                    <span className="text-xl">📈</span>
                                </div>
                                <div>
                                    <h1 className="text-lg font-bold text-dark-50">Stock Analyzer</h1>
                                    <p className="text-xs text-dark-400">Momentum Analysis Platform</p>
                                </div>
                            </div>

                            {/* Navigation */}
                            <nav className="hidden md:flex items-center gap-1">
                                {navItems.map((item) => (
                                    <NavLink
                                        key={item.path}
                                        to={item.path}
                                        className={({ isActive }) =>
                                            `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${isActive
                                                ? 'bg-primary-600/20 text-primary-400'
                                                : 'text-dark-300 hover:text-dark-100 hover:bg-dark-800'
                                            }`
                                        }
                                    >
                                        <span>{item.icon}</span>
                                        {item.label}
                                    </NavLink>
                                ))}
                            </nav>

                            {/* Time & Market Status */}
                            <div className="flex items-center gap-4">
                                <div className="text-right">
                                    <p className="text-sm font-medium text-dark-100">
                                        {currentTime.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
                                    </p>
                                    <p className="text-xs text-dark-400">
                                        {currentTime.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })}
                                    </p>
                                </div>
                                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${isMarketOpen(currentTime)
                                        ? 'bg-success-500/20 text-success-400'
                                        : 'bg-dark-700 text-dark-400'
                                    }`}>
                                    <span className={`w-2 h-2 rounded-full ${isMarketOpen(currentTime) ? 'bg-success-400 animate-pulse' : 'bg-dark-500'}`}></span>
                                    {isMarketOpen(currentTime) ? 'Market Open' : 'Market Closed'}
                                </div>
                            </div>
                        </div>
                    </div>
                </header>

                {/* Main Content */}
                <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/screener" element={<Screener />} />
                        <Route path="/signals" element={<Signals />} />
                        <Route path="/stock/:symbol" element={<StockDetail />} />
                    </Routes>
                </main>

                {/* Mobile Navigation */}
                <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-dark-900/95 backdrop-blur-xl border-t border-dark-700/50 z-50">
                    <div className="flex justify-around items-center h-16">
                        {navItems.map((item) => (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                className={({ isActive }) =>
                                    `flex flex-col items-center gap-1 px-4 py-2 ${isActive ? 'text-primary-400' : 'text-dark-400'
                                    }`
                                }
                            >
                                <span className="text-xl">{item.icon}</span>
                                <span className="text-xs">{item.label}</span>
                            </NavLink>
                        ))}
                    </div>
                </nav>
            </div>
        </Router>
    )
}

// Helper function to check if Indian market is open
function isMarketOpen(date) {
    const day = date.getDay()
    const hours = date.getHours()
    const minutes = date.getMinutes()
    const totalMinutes = hours * 60 + minutes

    // Weekend check
    if (day === 0 || day === 6) return false

    // Market hours: 9:15 AM to 3:30 PM IST
    const marketOpen = 9 * 60 + 15  // 9:15 AM
    const marketClose = 15 * 60 + 30 // 3:30 PM

    return totalMinutes >= marketOpen && totalMinutes <= marketClose
}

export default App

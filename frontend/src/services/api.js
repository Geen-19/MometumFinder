/**
 * API Service Layer
 * Centralized API communication with the backend
 */
import axios from 'axios'

const API_BASE = '/api'

// Create axios instance with default config
const api = axios.create({
    baseURL: API_BASE,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response?.data || error.message)
        throw error
    }
)

/**
 * API Methods
 */
const apiService = {
    // Health check
    health: async () => {
        const response = await api.get('/health')
        return response.data
    },

    // Get market overview for dashboard
    getMarketOverview: async () => {
        const response = await api.get('/market-overview')
        return response.data
    },

    // Get stock screener data
    getScreener: async (params = {}) => {
        const response = await api.get('/screener', { params })
        return response.data
    },

    // Get single stock details
    getStockDetail: async (symbol) => {
        const response = await api.get(`/stock/${symbol}`)
        return response.data
    },

    // Get signal recommendations
    getSignals: async (params = {}) => {
        const response = await api.get('/signals', { params })
        return response.data
    },

    // Get Nifty 50 data
    getNifty: async () => {
        const response = await api.get('/nifty')
        return response.data
    },

    // Get sector performance
    getSectors: async () => {
        const response = await api.get('/sectors')
        return response.data
    },

    // Get top movers
    getTopMovers: async (limit = 10) => {
        const response = await api.get('/top-movers', { params: { limit } })
        return response.data
    },

    // Search stocks
    searchStocks: async (query) => {
        const response = await api.get('/search', { params: { q: query } })
        return response.data
    },
}

export default apiService

// Helper functions
export const formatNumber = (num, decimals = 2) => {
    if (num === null || num === undefined) return '-'
    return Number(num).toFixed(decimals)
}

export const formatPercent = (num, showSign = true) => {
    if (num === null || num === undefined) return '-'
    const formatted = Number(num).toFixed(2)
    if (showSign && num > 0) return `+${formatted}%`
    return `${formatted}%`
}

export const formatLargeNumber = (num) => {
    if (num === null || num === undefined) return '-'
    if (num >= 10000000) return `${(num / 10000000).toFixed(2)} Cr`
    if (num >= 100000) return `${(num / 100000).toFixed(2)} L`
    if (num >= 1000) return `${(num / 1000).toFixed(2)} K`
    return num.toString()
}

export const getSignalColor = (signalType) => {
    switch (signalType) {
        case 'Strong Buy':
            return 'text-success-400 bg-success-500/20'
        case 'Buy':
            return 'text-success-500 bg-success-500/10'
        case 'Hold':
            return 'text-warning-400 bg-warning-500/20'
        case 'Sell':
            return 'text-danger-400 bg-danger-500/20'
        case 'Avoid':
            return 'text-danger-500 bg-danger-500/10'
        default:
            return 'text-dark-400 bg-dark-700'
    }
}

export const getScoreColor = (score) => {
    if (score >= 80) return 'from-success-500 to-success-400'
    if (score >= 70) return 'from-success-600 to-success-500'
    if (score >= 50) return 'from-warning-500 to-warning-400'
    if (score >= 40) return 'from-warning-600 to-warning-500'
    return 'from-danger-500 to-danger-400'
}

export const formatPrice = (num) => {
    if (num === null || num === undefined) return '-'
    return `₹${Number(num).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

// Export the raw axios instance for direct calls
export const apiClient = api


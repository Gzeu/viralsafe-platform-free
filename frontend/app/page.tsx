'use client'

import { useState, useEffect } from 'react'
import { Shield, AlertTriangle, CheckCircle, TrendingUp, Users, Globe, ExternalLink, Database, Activity, Clock, Zap, Eye, FileText, AlertCircle, Brain } from 'lucide-react'
import AdvancedSecurity from '../components/AdvancedSecurity'
import dynamic from 'next/dynamic'

// Dynamically import ClientThemeToggle to prevent SSR issues
const ClientThemeToggle = dynamic(
  () => import('../components/ClientThemeToggle').then((mod) => ({ default: mod.ClientThemeToggle })),
  { 
    ssr: false,
    loading: () => (
      <button className="relative p-2 rounded-lg bg-gray-100 dark:bg-gray-800 opacity-50 cursor-not-allowed transition-all duration-300">
        <div className="w-5 h-5" />
      </button>
    )
  }
)

interface AnalysisResult {
  id: string
  content_hash: string
  content_preview: string
  risk_score: number
  risk_level: string
  categories: string[]
  indicators: string[]
  recommendations: string[]
  platform: string
  timestamp: string
  processing_time_ms: number
  virustotal_report?: {
    url: string
    risk_score: number
    total_engines: number
    malicious: number
    suspicious: number
    clean: number
    scan_date: string
    reputation: number
  }
}

interface Analytics {
  total_analyses: number
  risk_distribution: { [key: string]: number }
  platform_stats: { [key: string]: number }
  avg_risk_score: number
  database_status: string
}

interface HealthStatus {
  status: string
  timestamp: string
  version: string
  environment: string
  services: {
    database: {
      status: string
      response_time_ms?: number
      collections?: { [key: string]: number }
    }
    virustotal: {
      status: string
      response_time_ms?: number
      rate_limit_remaining?: number
      quotas?: {
        api_requests_daily?: {
          used: number
          allowed: number
        }
      }
    }
  }
  uptime_info: {
    analyses_processed: number
    memory_usage: number
    port: number
  }
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://viralsafe-platform-free-api.onrender.com'

export default function Home() {
  const [content, setContent] = useState('')
  const [url, setUrl] = useState('')
  const [platform, setPlatform] = useState('general')
  const [checkUrls, setCheckUrls] = useState(true)
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<'analyze' | 'advanced' | 'health' | 'analytics'>('analyze')

  // Load initial data
  useEffect(() => {
    loadAnalytics()
    loadHealth()
    
    // Auto-refresh health every 30 seconds
    const interval = setInterval(loadHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  const analyzeContent = async () => {
    if (!content.trim()) return
    
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          content: content.trim(), 
          platform,
          url: url.trim() || undefined,
          check_urls: checkUrls,
          user_agent: navigator.userAgent 
        })
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }))
        throw new Error(`Analysis failed: ${errorData.detail || response.statusText}`)
      }
      
      const result = await response.json()
      setAnalysis(result)
      
      // Refresh analytics after new analysis
      setTimeout(loadAnalytics, 1000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
      console.error('Analysis error:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadAnalytics = async () => {
    try {
      const response = await fetch(`${API_URL}/analytics`)
      if (response.ok) {
        const data = await response.json()
        setAnalytics(data)
      }
    } catch (err) {
      console.error('Failed to load analytics:', err)
    }
  }

  const loadHealth = async () => {
    try {
      const response = await fetch(`${API_URL}/health`)
      if (response.ok) {
        const data = await response.json()
        setHealth(data)
      }
    } catch (err) {
      console.error('Failed to load health status:', err)
    }
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-red-600 dark:text-red-400'
      case 'medium': return 'text-yellow-600 dark:text-yellow-400' 
      case 'low': return 'text-green-600 dark:text-green-400'
      default: return 'text-gray-600 dark:text-gray-400'
    }
  }

  const getRiskBgColor = (level: string) => {
    switch (level) {
      case 'high': return 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800'
      case 'medium': return 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800'
      case 'low': return 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800'
      default: return 'bg-gray-50 border-gray-200 dark:bg-gray-800 dark:border-gray-700'
    }
  }

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'high': return <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400" />
      case 'medium': return <AlertTriangle className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
      case 'low': return <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
      default: return <Shield className="w-6 h-6 text-gray-600 dark:text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'connected': return 'text-green-600 dark:text-green-400'
      case 'degraded': return 'text-yellow-600 dark:text-yellow-400'
      case 'error': return 'text-red-600 dark:text-red-400'
      default: return 'text-gray-600 dark:text-gray-400'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'connected': return '🟢'
      case 'degraded': return '🟡'
      case 'error': return '🔴'
      default: return '⚪'
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-300">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">ViralSafe Platform v3.1</h1>
                <p className="text-sm text-gray-600 dark:text-gray-300">Enhanced AI-Powered Content Safety Analysis with Dark Mode</p>
              </div>
            </div>
            <div className="flex items-center space-x-6">
              <ClientThemeToggle />
              {health && (
                <div className="flex items-center space-x-2 text-sm">
                  <span className={getStatusColor(health.status)}>●</span>
                  <span className="text-gray-700 dark:text-gray-300">System {health.status}</span>
                  <span className="text-xs bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-2 py-1 rounded-full">
                    v{health.version || '3.1.0'} Enhanced
                  </span>
                </div>
              )}
              <div className="text-right text-sm text-gray-500 dark:text-gray-400">
                <div>🛡️ MongoDB + VirusTotal + AI</div>
                <div>🌍 Open Source Enhanced</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Navigation Tabs */}
        <div className="flex space-x-1 mb-8 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg transition-colors duration-300">
          <button
            onClick={() => setActiveTab('analyze')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'analyze'
                ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
            }`}
          >
            <Shield className="w-4 h-4 inline mr-2" />
            Content Analysis
          </button>
          <button
            onClick={() => setActiveTab('advanced')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'advanced'
                ? 'bg-white dark:bg-gray-600 text-purple-600 dark:text-purple-400 shadow-sm'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
            }`}
          >
            <Brain className="w-4 h-4 inline mr-2" />
            🔒 Advanced Security
          </button>
          <button
            onClick={() => setActiveTab('health')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'health'
                ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
            }`}
          >
            <Activity className="w-4 h-4 inline mr-2" />
            System Health
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'analytics'
                ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
            }`}
          >
            <TrendingUp className="w-4 h-4 inline mr-2" />
            Analytics
          </button>
        </div>

        {/* Content Analysis Tab */}
        {activeTab === 'analyze' && (
          <div className="space-y-8">
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 border border-gray-200 dark:border-gray-700 transition-colors duration-300">
                <div className="flex items-center">
                  <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400 mr-2" />
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Total Analyses</div>
                    <div className="text-xl font-bold text-gray-900 dark:text-white">{analytics?.total_analyses || 0}</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 border border-gray-200 dark:border-gray-700 transition-colors duration-300">
                <div className="flex items-center">
                  <Users className="w-5 h-5 text-green-600 dark:text-green-400 mr-2" />
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Avg Risk Score</div>
                    <div className="text-xl font-bold text-gray-900 dark:text-white">{analytics ? (analytics.avg_risk_score * 100).toFixed(1) : '0.0'}%</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 border border-gray-200 dark:border-gray-700 transition-colors duration-300">
                <div className="flex items-center">
                  <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 mr-2" />
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">High Risk</div>
                    <div className="text-xl font-bold text-gray-900 dark:text-white">{analytics?.risk_distribution?.high || 0}</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 border border-gray-200 dark:border-gray-700 transition-colors duration-300">
                <div className="flex items-center">
                  <Database className="w-5 h-5 text-purple-600 dark:text-purple-400 mr-2" />
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Storage</div>
                    <div className="text-sm font-medium text-gray-900 dark:text-white">{analytics?.database_status || 'Unknown'}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Main Analysis Form */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 transition-colors duration-300">
              <h2 className="text-xl font-semibold mb-6 flex items-center text-gray-900 dark:text-white">
                <Shield className="w-5 h-5 mr-2 text-blue-600 dark:text-blue-400" />
                Analyze Content Safety
              </h2>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Content to Analyze
                  </label>
                  <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="Paste content, message, post, or URL here to check for safety risks, scams, misinformation, phishing attempts..."
                    className="w-full h-32 p-4 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-colors duration-300"
                    maxLength={5000}
                  />
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {content.length}/5000 characters
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Source URL (Optional)
                    </label>
                    <input
                      type="url"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      placeholder="https://example.com/suspicious-link"
                      className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-colors duration-300"
                    />
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Enable VirusTotal URL scanning for enhanced security
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Platform
                    </label>
                    <select
                      value={platform}
                      onChange={(e) => setPlatform(e.target.value)}
                      className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors duration-300"
                    >
                      <option value="general">General Content</option>
                      <option value="twitter">Twitter/X</option>
                      <option value="facebook">Facebook</option>
                      <option value="telegram">Telegram</option>
                      <option value="whatsapp">WhatsApp</option>
                      <option value="instagram">Instagram</option>
                      <option value="tiktok">TikTok</option>
                      <option value="linkedin">LinkedIn</option>
                      <option value="email">Email</option>
                      <option value="sms">SMS</option>
                    </select>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={checkUrls}
                      onChange={(e) => setCheckUrls(e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700"
                    />
                    <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                      Enable VirusTotal URL scanning (recommended)
                    </span>
                  </label>
                </div>

                <button
                  onClick={analyzeContent}
                  disabled={loading || !content.trim()}
                  className="w-full px-6 py-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg flex items-center justify-center space-x-2 transition-colors duration-300 dark:bg-blue-500 dark:hover:bg-blue-600"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Analyzing with AI + VirusTotal...</span>
                    </>
                  ) : (
                    <>
                      <Shield className="w-5 h-5" />
                      <span>Analyze Content Safety</span>
                    </>
                  )}
                </button>
              </div>

              {error && (
                <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300 flex items-center transition-colors duration-300">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  <span>{error}</span>
                </div>
              )}
            </div>

            {/* Analysis Results */}
            {analysis && (
              <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-lg border-2 p-6 transition-colors duration-300 ${getRiskBgColor(analysis.risk_level)}`}>
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold flex items-center text-gray-900 dark:text-white">
                    {getRiskIcon(analysis.risk_level)}
                    <span className="ml-2">Analysis Results</span>
                  </h3>
                  <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center space-x-2">
                    <Clock className="w-4 h-4" />
                    <span>{analysis.processing_time_ms}ms</span>
                    <span>•</span>
                    <span>ID: {analysis.id}</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                  {/* Risk Assessment */}
                  <div className="space-y-6">
                    <div>
                      <h4 className="font-medium mb-3 flex items-center text-gray-900 dark:text-white">
                        <Zap className="w-4 h-4 mr-2" />
                        Risk Assessment
                      </h4>
                      <div className="flex items-center space-x-4">
                        <div className={`text-4xl font-bold ${getRiskColor(analysis.risk_level)}`}>
                          {(analysis.risk_score * 100).toFixed(1)}%
                        </div>
                        <div>
                          <div className={`font-medium uppercase text-sm ${getRiskColor(analysis.risk_level)}`}>
                            {analysis.risk_level} RISK
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            Platform: {analysis.platform}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-2 text-gray-900 dark:text-white">Risk Categories</h4>
                      <div className="flex flex-wrap gap-2">
                        {analysis.categories.map((cat, idx) => (
                          <span key={idx} className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full text-sm font-medium text-gray-900 dark:text-white transition-colors duration-300">
                            {cat.replace(/_/g, ' ').toUpperCase()}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-2 text-gray-900 dark:text-white">Risk Indicators</h4>
                      <div className="space-y-2">
                        {analysis.indicators.map((indicator, idx) => (
                          <div key={idx} className="text-sm text-gray-700 dark:text-gray-300 flex items-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded transition-colors duration-300">
                            <span className="w-2 h-2 bg-red-400 rounded-full mr-3 flex-shrink-0"></span>
                            <span>{indicator}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* VirusTotal Report */}
                    {analysis.virustotal_report && (
                      <div>
                        <h4 className="font-medium mb-2 flex items-center text-gray-900 dark:text-white">
                          <ExternalLink className="w-4 h-4 mr-2" />
                          VirusTotal URL Analysis
                        </h4>
                        <div className="bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg space-y-2 transition-colors duration-300">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600 dark:text-gray-400">Risk Score:</span>
                            <span className={`font-medium ${getRiskColor(analysis.virustotal_report.risk_score > 0.7 ? 'high' : analysis.virustotal_report.risk_score > 0.3 ? 'medium' : 'low')}`}>
                              {(analysis.virustotal_report.risk_score * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600 dark:text-gray-400">Engines:</span>
                            <span className="text-gray-900 dark:text-white">{analysis.virustotal_report.total_engines}</span>
                          </div>
                          <div className="grid grid-cols-3 gap-2 text-xs">
                            <div className="text-red-600 dark:text-red-400">❌ {analysis.virustotal_report.malicious}</div>
                            <div className="text-yellow-600 dark:text-yellow-400">⚠️ {analysis.virustotal_report.suspicious}</div>
                            <div className="text-green-600 dark:text-green-400">✅ {analysis.virustotal_report.clean}</div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Recommendations */}
                  <div>
                    <h4 className="font-medium mb-3 flex items-center text-gray-900 dark:text-white">
                      <Eye className="w-4 h-4 mr-2" />
                      Safety Recommendations
                    </h4>
                    <div className="space-y-3">
                      {analysis.recommendations.map((rec, idx) => (
                        <div key={idx} className="p-3 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 text-sm text-gray-900 dark:text-white transition-colors duration-300">
                          {rec}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Content Preview */}
                <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-600">
                  <h4 className="font-medium mb-2 flex items-center text-gray-900 dark:text-white">
                    <FileText className="w-4 h-4 mr-2" />
                    Analyzed Content
                  </h4>
                  <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 text-sm font-mono break-all text-gray-900 dark:text-white transition-colors duration-300">
                    {analysis.content_preview}
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
                    <span>Hash: {analysis.content_hash}</span>
                    <span>{new Date(analysis.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Advanced Security Tab */}
        {activeTab === 'advanced' && <AdvancedSecurity />}

        {/* System Health Tab */}
        {activeTab === 'health' && health && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 transition-colors duration-300">
              <h2 className="text-xl font-semibold mb-4 flex items-center text-gray-900 dark:text-white">
                <Activity className="w-5 h-5 mr-2 text-green-600 dark:text-green-400" />
                System Health Status v3.1
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg transition-colors duration-300">
                  <div className="text-2xl mb-2">{getStatusIcon(health.status)}</div>
                  <div className="font-medium text-gray-900 dark:text-white">Overall Status</div>
                  <div className={`text-sm ${getStatusColor(health.status)}`}>
                    {health.status.toUpperCase()}
                  </div>
                </div>
                
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg transition-colors duration-300">
                  <div className="text-2xl mb-2">🏗️</div>
                  <div className="font-medium text-gray-900 dark:text-white">Environment</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {health.environment}
                  </div>
                </div>
                
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg transition-colors duration-300">
                  <div className="text-2xl mb-2">📊</div>
                  <div className="font-medium text-gray-900 dark:text-white">Analyses</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {health.uptime_info.analyses_processed}
                  </div>
                </div>
                
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg transition-colors duration-300">
                  <div className="text-2xl mb-2">🔌</div>
                  <div className="font-medium text-gray-900 dark:text-white">Port</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {health.uptime_info.port}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Database Status */}
                <div className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 transition-colors duration-300">
                  <h3 className="font-medium mb-3 flex items-center text-gray-900 dark:text-white">
                    <Database className="w-4 h-4 mr-2" />
                    MongoDB Atlas
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Status:</span>
                      <span className={getStatusColor(health.services.database.status)}>
                        {getStatusIcon(health.services.database.status)} {health.services.database.status}
                      </span>
                    </div>
                    {health.services.database.response_time_ms && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Response Time:</span>
                        <span className="text-gray-900 dark:text-white">{health.services.database.response_time_ms.toFixed(2)}ms</span>
                      </div>
                    )}
                    {health.services.database.collections && (
                      <div className="mt-3">
                        <div className="font-medium mb-2 text-gray-900 dark:text-white">Collections:</div>
                        {Object.entries(health.services.database.collections).map(([name, count]) => (
                          <div key={name} className="flex justify-between">
                            <span className="pl-2 text-gray-600 dark:text-gray-400">{name}:</span>
                            <span className="text-gray-900 dark:text-white">{count} documents</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* VirusTotal Status */}
                <div className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 transition-colors duration-300">
                  <h3 className="font-medium mb-3 flex items-center text-gray-900 dark:text-white">
                    <Shield className="w-4 h-4 mr-2" />
                    VirusTotal API
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Status:</span>
                      <span className={getStatusColor(health.services.virustotal.status)}>
                        {getStatusIcon(health.services.virustotal.status)} {health.services.virustotal.status}
                      </span>
                    </div>
                    {health.services.virustotal.response_time_ms && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Response Time:</span>
                        <span className="text-gray-900 dark:text-white">{health.services.virustotal.response_time_ms.toFixed(2)}ms</span>
                      </div>
                    )}
                    {health.services.virustotal.rate_limit_remaining !== undefined && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Rate Limit:</span>
                        <span className="text-gray-900 dark:text-white">{health.services.virustotal.rate_limit_remaining}/4 per min</span>
                      </div>
                    )}
                    {health.services.virustotal.quotas?.api_requests_daily && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Daily Quota:</span>
                        <span className="text-gray-900 dark:text-white">
                          {health.services.virustotal.quotas.api_requests_daily.used}/
                          {health.services.virustotal.quotas.api_requests_daily.allowed}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="mt-4 text-xs text-gray-500 dark:text-gray-400 text-center">
                Last updated: {new Date(health.timestamp).toLocaleString()}
                <button 
                  onClick={loadHealth}
                  className="ml-4 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                >
                  Refresh
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 transition-colors duration-300">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold flex items-center text-gray-900 dark:text-white">
                  <TrendingUp className="w-5 h-5 mr-2 text-blue-600 dark:text-blue-400" />
                  Platform Analytics v3.1
                </h2>
                <button
                  onClick={loadAnalytics}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white rounded-lg text-sm transition-colors duration-300"
                >
                  Refresh Data
                </button>
              </div>
              
              {analytics ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {/* Risk Distribution */}
                  <div className="col-span-1 md:col-span-2 lg:col-span-1">
                    <h3 className="font-medium mb-3 text-gray-900 dark:text-white">Risk Distribution</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center p-2 bg-red-50 dark:bg-red-900/20 rounded transition-colors duration-300">
                        <span className="text-red-700 dark:text-red-300">High Risk</span>
                        <span className="font-bold text-red-700 dark:text-red-300">{analytics.risk_distribution.high || 0}</span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded transition-colors duration-300">
                        <span className="text-yellow-700 dark:text-yellow-300">Medium Risk</span>
                        <span className="font-bold text-yellow-700 dark:text-yellow-300">{analytics.risk_distribution.medium || 0}</span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-green-50 dark:bg-green-900/20 rounded transition-colors duration-300">
                        <span className="text-green-700 dark:text-green-300">Low Risk</span>
                        <span className="font-bold text-green-700 dark:text-green-300">{analytics.risk_distribution.low || 0}</span>
                      </div>
                    </div>
                  </div>

                  {/* Platform Stats */}
                  <div className="col-span-1 md:col-span-2 lg:col-span-1">
                    <h3 className="font-medium mb-3 text-gray-900 dark:text-white">Platform Usage</h3>
                    <div className="space-y-2">
                      {Object.entries(analytics.platform_stats || {}).map(([platform, count]) => (
                        <div key={platform} className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded transition-colors duration-300">
                          <span className="capitalize text-gray-900 dark:text-white">{platform}</span>
                          <span className="font-bold text-gray-900 dark:text-white">{count}</span>
                        </div>
                      ))}
                      {Object.keys(analytics.platform_stats || {}).length === 0 && (
                        <div className="text-gray-500 dark:text-gray-400 text-sm">No platform data available</div>
                      )}
                    </div>
                  </div>

                  {/* Summary Stats */}
                  <div className="col-span-1 md:col-span-2 lg:col-span-1">
                    <h3 className="font-medium mb-3 text-gray-900 dark:text-white">Enhanced Summary</h3>
                    <div className="space-y-4">
                      <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg transition-colors duration-300">
                        <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                          {analytics.total_analyses}
                        </div>
                        <div className="text-sm text-blue-700 dark:text-blue-300">Total Enhanced Analyses</div>
                      </div>
                      <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg transition-colors duration-300">
                        <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                          {(analytics.avg_risk_score * 100).toFixed(1)}%
                        </div>
                        <div className="text-sm text-purple-700 dark:text-purple-300">Avg Risk Score v3.1</div>
                      </div>
                      <div className="text-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg transition-colors duration-300">
                        <div className="text-lg font-bold text-gray-600 dark:text-gray-400">
                          {analytics.database_status}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">Enhanced Storage Status</div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Loading enhanced analytics data...</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-500 dark:text-gray-400 space-y-2">
          <div className="flex justify-center space-x-6 text-sm">
            <a href={`${API_URL}/docs`} target="_blank" className="hover:text-blue-600 dark:hover:text-blue-400 flex items-center transition-colors duration-300">
              <ExternalLink className="w-3 h-3 mr-1" />API Docs
            </a>
            <a href="https://github.com/Gzeu/viralsafe-platform-free" target="_blank" className="hover:text-blue-600 dark:hover:text-blue-400 flex items-center transition-colors duration-300">
              <ExternalLink className="w-3 h-3 mr-1" />GitHub
            </a>
            <a href={`${API_URL}/health`} target="_blank" className="hover:text-blue-600 dark:hover:text-blue-400 flex items-center transition-colors duration-300">
              <ExternalLink className="w-3 h-3 mr-1" />Health Check
            </a>
          </div>
          <p className="text-sm">
            🛡️ ViralSafe Platform v3.1 Enhanced with Dark Mode • MongoDB Atlas + VirusTotal API + Multi-AI • Open Source • Built with ❤️ for Internet Safety
          </p>
          <p className="text-xs">
            Backend: Render.com • Frontend: Vercel • Database: MongoDB Atlas • Security: VirusTotal • AI: Groq + Enhanced Features • Theme: Light/Dark Mode
          </p>
        </footer>
      </div>
    </main>
  )
}
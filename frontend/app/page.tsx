'use client'

import { useState, useEffect } from 'react'
import { Shield, AlertTriangle, CheckCircle, TrendingUp, Users, Globe, ExternalLink, Database, Activity, Clock, Zap, Eye, FileText, AlertCircle } from 'lucide-react'

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
  const [activeTab, setActiveTab] = useState<'analyze' | 'health' | 'analytics'>('analyze')

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
      case 'high': return 'text-red-600'
      case 'medium': return 'text-yellow-600' 
      case 'low': return 'text-green-600'
      default: return 'text-gray-600'
    }
  }

  const getRiskBgColor = (level: string) => {
    switch (level) {
      case 'high': return 'bg-red-50 border-red-200'
      case 'medium': return 'bg-yellow-50 border-yellow-200'
      case 'low': return 'bg-green-50 border-green-200'
      default: return 'bg-gray-50 border-gray-200'
    }
  }

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'high': return <AlertTriangle className="w-6 h-6 text-red-600" />
      case 'medium': return <AlertTriangle className="w-6 h-6 text-yellow-600" />
      case 'low': return <CheckCircle className="w-6 h-6 text-green-600" />
      default: return <Shield className="w-6 h-6 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'connected': return 'text-green-600'
      case 'degraded': return 'text-yellow-600'
      case 'error': return 'text-red-600'
      default: return 'text-gray-600'
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
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">ViralSafe Platform</h1>
                <p className="text-sm text-gray-600">Advanced Content Safety Analysis with AI</p>
              </div>
            </div>
            <div className="flex items-center space-x-6">
              {health && (
                <div className="flex items-center space-x-2 text-sm">
                  <span className={getStatusColor(health.status)}>●</span>
                  <span>System {health.status}</span>
                </div>
              )}
              <div className="text-right text-sm text-gray-500">
                <div>🛡️ MongoDB + VirusTotal</div>
                <div>🌍 Open Source</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Navigation Tabs */}
        <div className="flex space-x-1 mb-8 bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('analyze')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'analyze'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Shield className="w-4 h-4 inline mr-2" />
            Content Analysis
          </button>
          <button
            onClick={() => setActiveTab('health')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'health'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Activity className="w-4 h-4 inline mr-2" />
            System Health
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'analytics'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
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
              <div className="bg-white rounded-lg shadow-sm p-4 border">
                <div className="flex items-center">
                  <TrendingUp className="w-5 h-5 text-blue-600 mr-2" />
                  <div>
                    <div className="text-sm text-gray-600">Total Analyses</div>
                    <div className="text-xl font-bold">{analytics?.total_analyses || 0}</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm p-4 border">
                <div className="flex items-center">
                  <Users className="w-5 h-5 text-green-600 mr-2" />
                  <div>
                    <div className="text-sm text-gray-600">Avg Risk Score</div>
                    <div className="text-xl font-bold">{analytics ? (analytics.avg_risk_score * 100).toFixed(1) : '0.0'}%</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm p-4 border">
                <div className="flex items-center">
                  <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
                  <div>
                    <div className="text-sm text-gray-600">High Risk</div>
                    <div className="text-xl font-bold">{analytics?.risk_distribution?.high || 0}</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm p-4 border">
                <div className="flex items-center">
                  <Database className="w-5 h-5 text-purple-600 mr-2" />
                  <div>
                    <div className="text-sm text-gray-600">Storage</div>
                    <div className="text-sm font-medium">{analytics?.database_status || 'Unknown'}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Main Analysis Form */}
            <div className="bg-white rounded-xl shadow-lg border p-6">
              <h2 className="text-xl font-semibold mb-6 flex items-center">
                <Shield className="w-5 h-5 mr-2 text-blue-600" />
                Analyze Content Safety
              </h2>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Content to Analyze
                  </label>
                  <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="Paste content, message, post, or URL here to check for safety risks, scams, misinformation, phishing attempts..."
                    className="w-full h-32 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    maxLength={5000}
                  />
                  <div className="text-xs text-gray-500 mt-1">
                    {content.length}/5000 characters
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Source URL (Optional)
                    </label>
                    <input
                      type="url"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      placeholder="https://example.com/suspicious-link"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Enable VirusTotal URL scanning for enhanced security
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Platform
                    </label>
                    <select
                      value={platform}
                      onChange={(e) => setPlatform(e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
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
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">
                      Enable VirusTotal URL scanning (recommended)
                    </span>
                  </label>
                </div>

                <button
                  onClick={analyzeContent}
                  disabled={loading || !content.trim()}
                  className="w-full px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
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
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-center">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  <span>{error}</span>
                </div>
              )}
            </div>

            {/* Analysis Results */}
            {analysis && (
              <div className={`bg-white rounded-xl shadow-lg border-2 p-6 ${getRiskBgColor(analysis.risk_level)}`}>
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold flex items-center">
                    {getRiskIcon(analysis.risk_level)}
                    <span className="ml-2">Analysis Results</span>
                  </h3>
                  <div className="text-sm text-gray-500 flex items-center space-x-2">
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
                      <h4 className="font-medium mb-3 flex items-center">
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
                          <div className="text-sm text-gray-600">
                            Platform: {analysis.platform}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-2">Risk Categories</h4>
                      <div className="flex flex-wrap gap-2">
                        {analysis.categories.map((cat, idx) => (
                          <span key={idx} className="px-3 py-1 bg-gray-100 rounded-full text-sm font-medium">
                            {cat.replace(/_/g, ' ').toUpperCase()}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-2">Risk Indicators</h4>
                      <div className="space-y-2">
                        {analysis.indicators.map((indicator, idx) => (
                          <div key={idx} className="text-sm text-gray-700 flex items-center p-2 bg-gray-50 rounded">
                            <span className="w-2 h-2 bg-red-400 rounded-full mr-3 flex-shrink-0"></span>
                            <span>{indicator}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* VirusTotal Report */}
                    {analysis.virustotal_report && (
                      <div>
                        <h4 className="font-medium mb-2 flex items-center">
                          <ExternalLink className="w-4 h-4 mr-2" />
                          VirusTotal URL Analysis
                        </h4>
                        <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Risk Score:</span>
                            <span className={`font-medium ${getRiskColor(analysis.virustotal_report.risk_score > 0.7 ? 'high' : analysis.virustotal_report.risk_score > 0.3 ? 'medium' : 'low')}`}>
                              {(analysis.virustotal_report.risk_score * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Engines:</span>
                            <span>{analysis.virustotal_report.total_engines}</span>
                          </div>
                          <div className="grid grid-cols-3 gap-2 text-xs">
                            <div className="text-red-600">❌ {analysis.virustotal_report.malicious}</div>
                            <div className="text-yellow-600">⚠️ {analysis.virustotal_report.suspicious}</div>
                            <div className="text-green-600">✅ {analysis.virustotal_report.clean}</div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Recommendations */}
                  <div>
                    <h4 className="font-medium mb-3 flex items-center">
                      <Eye className="w-4 h-4 mr-2" />
                      Safety Recommendations
                    </h4>
                    <div className="space-y-3">
                      {analysis.recommendations.map((rec, idx) => (
                        <div key={idx} className="p-3 bg-white rounded-lg border text-sm">
                          {rec}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Content Preview */}
                <div className="mt-8 pt-6 border-t">
                  <h4 className="font-medium mb-2 flex items-center">
                    <FileText className="w-4 h-4 mr-2" />
                    Analyzed Content
                  </h4>
                  <div className="p-4 bg-gray-50 rounded-lg border text-sm font-mono break-all">
                    {analysis.content_preview}
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 mt-2">
                    <span>Hash: {analysis.content_hash}</span>
                    <span>{new Date(analysis.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* System Health Tab */}
        {activeTab === 'health' && health && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-lg border p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <Activity className="w-5 h-5 mr-2 text-green-600" />
                System Health Status
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl mb-2">{getStatusIcon(health.status)}</div>
                  <div className="font-medium">Overall Status</div>
                  <div className={`text-sm ${getStatusColor(health.status)}`}>
                    {health.status.toUpperCase()}
                  </div>
                </div>
                
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl mb-2">🏗️</div>
                  <div className="font-medium">Environment</div>
                  <div className="text-sm text-gray-600">
                    {health.environment}
                  </div>
                </div>
                
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl mb-2">📊</div>
                  <div className="font-medium">Analyses</div>
                  <div className="text-sm text-gray-600">
                    {health.uptime_info.analyses_processed}
                  </div>
                </div>
                
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl mb-2">🔌</div>
                  <div className="font-medium">Port</div>
                  <div className="text-sm text-gray-600">
                    {health.uptime_info.port}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Database Status */}
                <div className="border rounded-lg p-4">
                  <h3 className="font-medium mb-3 flex items-center">
                    <Database className="w-4 h-4 mr-2" />
                    MongoDB Atlas
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Status:</span>
                      <span className={getStatusColor(health.services.database.status)}>
                        {getStatusIcon(health.services.database.status)} {health.services.database.status}
                      </span>
                    </div>
                    {health.services.database.response_time_ms && (
                      <div className="flex justify-between">
                        <span>Response Time:</span>
                        <span>{health.services.database.response_time_ms.toFixed(2)}ms</span>
                      </div>
                    )}
                    {health.services.database.collections && (
                      <div className="mt-3">
                        <div className="font-medium mb-2">Collections:</div>
                        {Object.entries(health.services.database.collections).map(([name, count]) => (
                          <div key={name} className="flex justify-between">
                            <span className="pl-2">{name}:</span>
                            <span>{count} documents</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* VirusTotal Status */}
                <div className="border rounded-lg p-4">
                  <h3 className="font-medium mb-3 flex items-center">
                    <Shield className="w-4 h-4 mr-2" />
                    VirusTotal API
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Status:</span>
                      <span className={getStatusColor(health.services.virustotal.status)}>
                        {getStatusIcon(health.services.virustotal.status)} {health.services.virustotal.status}
                      </span>
                    </div>
                    {health.services.virustotal.response_time_ms && (
                      <div className="flex justify-between">
                        <span>Response Time:</span>
                        <span>{health.services.virustotal.response_time_ms.toFixed(2)}ms</span>
                      </div>
                    )}
                    {health.services.virustotal.rate_limit_remaining !== undefined && (
                      <div className="flex justify-between">
                        <span>Rate Limit:</span>
                        <span>{health.services.virustotal.rate_limit_remaining}/4 per min</span>
                      </div>
                    )}
                    {health.services.virustotal.quotas?.api_requests_daily && (
                      <div className="flex justify-between">
                        <span>Daily Quota:</span>
                        <span>
                          {health.services.virustotal.quotas.api_requests_daily.used}/
                          {health.services.virustotal.quotas.api_requests_daily.allowed}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="mt-4 text-xs text-gray-500 text-center">
                Last updated: {new Date(health.timestamp).toLocaleString()}
                <button 
                  onClick={loadHealth}
                  className="ml-4 text-blue-600 hover:text-blue-800"
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
            <div className="bg-white rounded-xl shadow-lg border p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
                  Platform Analytics
                </h2>
                <button
                  onClick={loadAnalytics}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                >
                  Refresh Data
                </button>
              </div>
              
              {analytics ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {/* Risk Distribution */}
                  <div className="col-span-1 md:col-span-2 lg:col-span-1">
                    <h3 className="font-medium mb-3">Risk Distribution</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center p-2 bg-red-50 rounded">
                        <span className="text-red-700">High Risk</span>
                        <span className="font-bold text-red-700">{analytics.risk_distribution.high || 0}</span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-yellow-50 rounded">
                        <span className="text-yellow-700">Medium Risk</span>
                        <span className="font-bold text-yellow-700">{analytics.risk_distribution.medium || 0}</span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-green-50 rounded">
                        <span className="text-green-700">Low Risk</span>
                        <span className="font-bold text-green-700">{analytics.risk_distribution.low || 0}</span>
                      </div>
                    </div>
                  </div>

                  {/* Platform Stats */}
                  <div className="col-span-1 md:col-span-2 lg:col-span-1">
                    <h3 className="font-medium mb-3">Platform Usage</h3>
                    <div className="space-y-2">
                      {Object.entries(analytics.platform_stats || {}).map(([platform, count]) => (
                        <div key={platform} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                          <span className="capitalize">{platform}</span>
                          <span className="font-bold">{count}</span>
                        </div>
                      ))}
                      {Object.keys(analytics.platform_stats || {}).length === 0 && (
                        <div className="text-gray-500 text-sm">No platform data available</div>
                      )}
                    </div>
                  </div>

                  {/* Summary Stats */}
                  <div className="col-span-1 md:col-span-2 lg:col-span-1">
                    <h3 className="font-medium mb-3">Summary</h3>
                    <div className="space-y-4">
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">
                          {analytics.total_analyses}
                        </div>
                        <div className="text-sm text-blue-700">Total Analyses</div>
                      </div>
                      <div className="text-center p-4 bg-purple-50 rounded-lg">
                        <div className="text-2xl font-bold text-purple-600">
                          {(analytics.avg_risk_score * 100).toFixed(1)}%
                        </div>
                        <div className="text-sm text-purple-700">Avg Risk Score</div>
                      </div>
                      <div className="text-center p-4 bg-gray-50 rounded-lg">
                        <div className="text-lg font-bold text-gray-600">
                          {analytics.database_status}
                        </div>
                        <div className="text-xs text-gray-600">Storage Status</div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Loading analytics data...</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-500 space-y-2">
          <div className="flex justify-center space-x-6 text-sm">
            <a href={`${API_URL}/docs`} target="_blank" className="hover:text-blue-600 flex items-center">
              <ExternalLink className="w-3 h-3 mr-1" />API Docs
            </a>
            <a href="https://github.com/Gzeu/viralsafe-platform-free" target="_blank" className="hover:text-blue-600 flex items-center">
              <ExternalLink className="w-3 h-3 mr-1" />GitHub
            </a>
            <a href={`${API_URL}/health`} target="_blank" className="hover:text-blue-600 flex items-center">
              <ExternalLink className="w-3 h-3 mr-1" />Health Check
            </a>
          </div>
          <p className="text-sm">
            🛡️ ViralSafe Platform • MongoDB Atlas + VirusTotal API • Open Source • Built with ❤️ for Internet Safety
          </p>
          <p className="text-xs">
            Backend: Render.com • Frontend: Vercel • Database: MongoDB Atlas • Security: VirusTotal
          </p>
        </footer>
      </div>
    </main>
  )
}
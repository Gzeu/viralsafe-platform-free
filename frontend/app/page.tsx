'use client'

import { useState } from 'react'
import { Shield, AlertTriangle, CheckCircle, TrendingUp, Users, Globe } from 'lucide-react'

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
}

interface Analytics {
  total_analyses: number
  risk_distribution: { [key: string]: number }
  platform_stats: { [key: string]: number }
  avg_risk_score: number
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Home() {
  const [content, setContent] = useState('')
  const [platform, setPlatform] = useState('general')
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

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
          user_agent: navigator.userAgent 
        })
      })
      
      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`)
      }
      
      const result = await response.json()
      setAnalysis(result)
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

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">ViralSafe Platform</h1>
                <p className="text-sm text-gray-600">Open Source Content Safety Analysis</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right text-sm text-gray-500">
                <div>🆓 Free Tier</div>
                <div>🌍 Open Source</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Analytics Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
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
          
          <button
            onClick={loadAnalytics}
            className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg p-4 flex items-center justify-center space-x-2"
          >
            <Globe className="w-5 h-5" />
            <span>Load Stats</span>
          </button>
        </div>

        {/* Main Analysis Form */}
        <div className="bg-white rounded-xl shadow-lg border p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Shield className="w-5 h-5 mr-2 text-blue-600" />
            Analyze Content Safety
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Content to Analyze
              </label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Paste content, message, post, or URL here to check for safety risks, scams, misinformation..."
                className="w-full h-32 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                maxLength={5000}
              />
              <div className="text-xs text-gray-500 mt-1">
                {content.length}/5000 characters
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Platform
                </label>
                <select
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="general">General</option>
                  <option value="twitter">Twitter/X</option>
                  <option value="facebook">Facebook</option>
                  <option value="telegram">Telegram</option>
                  <option value="whatsapp">WhatsApp</option>
                  <option value="instagram">Instagram</option>
                  <option value="tiktok">TikTok</option>
                  <option value="email">Email</option>
                  <option value="sms">SMS</option>
                </select>
              </div>

              <div className="flex items-end">
                <button
                  onClick={analyzeContent}
                  disabled={loading || !content.trim()}
                  className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <Shield className="w-4 h-4" />
                      <span>Analyze Content</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
              ❌ Error: {error}
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
              <div className="text-sm text-gray-500">
                ID: {analysis.id} • {analysis.processing_time_ms}ms
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Risk Assessment */}
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Risk Assessment</h4>
                  <div className="flex items-center space-x-4">
                    <div className={`text-3xl font-bold ${getRiskColor(analysis.risk_level)}`}>
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
                  <h4 className="font-medium mb-2">Categories</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysis.categories.map((cat, idx) => (
                      <span key={idx} className="px-3 py-1 bg-gray-100 rounded-full text-sm">
                        {cat.replace(/_/g, ' ').toUpperCase()}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2">Risk Indicators</h4>
                  <div className="space-y-1">
                    {analysis.indicators.map((indicator, idx) => (
                      <div key={idx} className="text-sm text-gray-700 flex items-center">
                        <span className="w-2 h-2 bg-red-400 rounded-full mr-2"></span>
                        {indicator}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Recommendations */}
              <div>
                <h4 className="font-medium mb-2">Safety Recommendations</h4>
                <div className="space-y-2">
                  {analysis.recommendations.map((rec, idx) => (
                    <div key={idx} className="p-3 bg-white rounded border text-sm">
                      {rec}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Content Preview */}
            <div className="mt-6 pt-6 border-t">
              <h4 className="font-medium mb-2">Analyzed Content</h4>
              <div className="p-3 bg-gray-50 rounded border text-sm font-mono">
                {analysis.content_preview}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Content Hash: {analysis.content_hash} • {analysis.timestamp}
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-500 space-y-2">
          <div className="flex justify-center space-x-6 text-sm">
            <a href={`${API_URL}/docs`} target="_blank" className="hover:text-blue-600">API Docs</a>
            <a href="https://github.com/Gzeu/viralsafe-platform-free" target="_blank" className="hover:text-blue-600">GitHub</a>
            <a href="#" className="hover:text-blue-600">Report Issue</a>
          </div>
          <p className="text-sm">
            🛡️ ViralSafe Platform • Open Source • Free Tier • Built with ❤️ for Internet Safety
          </p>
          <p className="text-xs">
            Running on Railway (Backend) + Vercel (Frontend) • Cost: $0/month
          </p>
        </footer>
      </div>
    </main>
  )
}
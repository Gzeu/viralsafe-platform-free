'use client'
import { useState } from 'react'
import AnalyzeForm from '../components/AnalyzeForm'
import BatchUploader from '../components/BatchUploader'
import AdvancedScanPanel from '../components/AdvancedScanPanel'
import { ExportButtons } from '../components/ExportButtons'

interface AnalysisResult {
  id: string
  risk: { score: number; level: string; reasons: string[] }
  provider: string
  flags: string[]
  url?: string
  advanced?: {
    confidence: number
    threatLevel: string
    analysis: {
      sentiment: number
      urgency: number
      deception: number
      financialRisk: number
    }
    detectedPatterns: string[]
    urlIntelligence?: {
      domain: string
      reputation: string
      riskScore: number
      threatCategories: string[]
    }
  }
}

export default function HomePage() {
  const [results, setResults] = useState<AnalysisResult[]>([])
  const [scanUrl, setScanUrl] = useState('')
  const [scanLoading, setScanLoading] = useState(false)
  const [scanResult, setScanResult] = useState<any>(null)
  const [analytics, setAnalytics] = useState<any>(null)
  const [activeTab, setActiveTab] = useState<'basic' | 'advanced'>('basic')

  const handleAnalyzeResult = (result: AnalysisResult) => {
    setResults(prev => [result, ...prev])
  }

  const handleBatchResults = (batchResults: AnalysisResult[]) => {
    setResults(prev => [...batchResults, ...prev])
  }

  const handleScan = async () => {
    if (!scanUrl.trim()) return
    setScanLoading(true)
    try {
      const res = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ url: scanUrl })
      })
      const json = await res.json()
      if (json.ok) {
        setScanResult(json.data)
      } else {
        alert('Eroare scan: ' + json.error)
      }
    } catch (e: any) {
      alert('Eroare: ' + e.message)
    } finally {
      setScanLoading(false)
    }
  }

  const loadAnalytics = async () => {
    try {
      const res = await fetch('/api/analytics')
      const json = await res.json()
      if (json.ok) setAnalytics(json.data)
    } catch (e) {
      console.error('Failed to load analytics:', e)
    }
  }

  return (
    <div className="space-y-8">
      {/* Header with Tab Navigation */}
      <div className="bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">🛡️ ViralSafe Security Platform</h1>
            <p className="text-gray-300">AI-powered threat detection and content analysis</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('basic')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'basic' 
                  ? 'bg-blue-600 text-white shadow-lg' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              🔍 Basic Analysis
            </button>
            <button
              onClick={() => setActiveTab('advanced')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'advanced' 
                  ? 'bg-purple-600 text-white shadow-lg' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              🔒 Advanced Security
            </button>
          </div>
        </div>
        
        {/* Feature Indicators */}
        <div className="flex flex-wrap gap-2 text-xs">
          <span className="px-2 py-1 rounded bg-blue-500/20 text-blue-300">⚛️ React + Next.js</span>
          <span className="px-2 py-1 rounded bg-green-500/20 text-green-300">🤖 Multi-AI Analysis</span>
          <span className="px-2 py-1 rounded bg-purple-500/20 text-purple-300">🌐 URL Intelligence</span>
          <span className="px-2 py-1 rounded bg-red-500/20 text-red-300">🛡️ Threat Detection</span>
          <span className="px-2 py-1 rounded bg-yellow-500/20 text-yellow-300">📊 Real-time Analytics</span>
        </div>
      </div>

      {/* Analytics Panel */}
      <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-white">📊 Platform Statistics</h2>
          <button onClick={loadAnalytics} className="btn-secondary text-sm">Refresh Stats</button>
        </div>
        {analytics && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
            <div className="bg-blue-500/20 p-4 rounded">
              <div className="text-2xl font-bold text-blue-300">{analytics.totalAnalyses}</div>
              <div className="text-sm text-gray-300">Total Scans</div>
            </div>
            <div className="bg-red-500/20 p-4 rounded">
              <div className="text-2xl font-bold text-red-300">{analytics.distribution.high}</div>
              <div className="text-sm text-gray-300">High Risk</div>
            </div>
            <div className="bg-yellow-500/20 p-4 rounded">
              <div className="text-2xl font-bold text-yellow-300">{analytics.distribution.medium}</div>
              <div className="text-sm text-gray-300">Medium Risk</div>
            </div>
            <div className="bg-green-500/20 p-4 rounded">
              <div className="text-2xl font-bold text-green-300">{analytics.distribution.low}</div>
              <div className="text-sm text-gray-300">Low Risk</div>
            </div>
            <div className="bg-purple-500/20 p-4 rounded">
              <div className="text-2xl font-bold text-purple-300">{analytics.scans}</div>
              <div className="text-sm text-gray-300">URL Scans</div>
            </div>
          </div>
        )}
      </div>

      {/* Main Content - Tabbed */}
      {activeTab === 'basic' ? (
        <>
          {/* Basic Analysis Tools */}
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">🔍 Quick Analysis</h2>
              <AnalyzeForm onResult={handleAnalyzeResult} />
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">🌐 VirusTotal Scan</h2>
              <div className="space-y-3">
                <input 
                  value={scanUrl} 
                  onChange={e => setScanUrl(e.target.value)}
                  className="w-full p-3 rounded bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
                  placeholder="https://example.com"
                />
                <button 
                  disabled={scanLoading} 
                  onClick={handleScan}
                  className="w-full btn-primary disabled:opacity-50"
                >
                  {scanLoading ? 'Scanning...' : 'Scan with VirusTotal'}
                </button>
                {scanResult && (
                  <div className={`p-3 rounded ${scanResult.verdict === 'malicious' ? 'bg-red-500/20 text-red-300' : 'bg-green-500/20 text-green-300'}`}>
                    <strong>Verdict:</strong> {scanResult.verdict}
                    <br />
                    <strong>Risk:</strong> {scanResult.risk.level} ({scanResult.risk.score}%)
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Batch Upload */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">📋 Batch Processing</h2>
            <BatchUploader onBatch={handleBatchResults} />
          </div>
        </>
      ) : (
        <>
          {/* Advanced Security Features */}
          <AdvancedScanPanel />
          
          {/* Advanced Features Info */}
          <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 backdrop-blur-sm rounded-lg p-6 border border-purple-500/30">
            <h2 className="text-xl font-semibold text-white mb-4">✨ Advanced Security Features</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-purple-300 mb-2">🤖 Multi-Layer AI Analysis</h3>
                <ul className="text-sm text-gray-300 space-y-1">
                  <li>• OpenAI GPT-3.5 Turbo integration</li>
                  <li>• Groq Mixtral-8x7B analysis</li>
                  <li>• Google Gemini Pro detection</li>
                  <li>• Ensemble AI consensus scoring</li>
                  <li>• Advanced heuristic fallbacks</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-blue-300 mb-2">🌐 URL Intelligence & Threat DB</h3>
                <ul className="text-sm text-gray-300 space-y-1">
                  <li>• Domain reputation analysis</li>
                  <li>• URL shortener detection</li>
                  <li>• Malicious domain database</li>
                  <li>• Certificate validation</li>
                  <li>• VirusTotal integration</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-green-300 mb-2">🔎 Social Engineering Detection</h3>
                <ul className="text-sm text-gray-300 space-y-1">
                  <li>• Urgency tactic identification</li>
                  <li>• Fear and greed exploitation</li>
                  <li>• Authority impersonation</li>
                  <li>• Scarcity manipulation</li>
                  <li>• Financial risk assessment</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-red-300 mb-2">📊 Advanced Analytics</h3>
                <ul className="text-sm text-gray-300 space-y-1">
                  <li>• Confidence scoring</li>
                  <li>• Multi-factor risk assessment</li>
                  <li>• Pattern recognition</li>
                  <li>• Threat level classification</li>
                  <li>• Security recommendations</li>
                </ul>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-white">📋 Analysis Results ({results.length})</h2>
            <ExportButtons data={results} />
          </div>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {results.map((result, i) => (
              <div key={result.id} className={`p-4 rounded border ${
                result.risk.level === 'critical' ? 'bg-red-500/20 border-red-500' :
                result.risk.level === 'high' ? 'bg-red-500/20 border-red-500' :
                result.risk.level === 'medium' ? 'bg-yellow-500/20 border-yellow-500' :
                'bg-green-500/20 border-green-500'
              }`}>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="font-medium text-white flex items-center gap-2">
                      <span>Risk: {result.risk.level} ({result.risk.score}%)</span>
                      {result.advanced && (
                        <span className="text-xs px-2 py-1 rounded bg-purple-600/50 text-purple-200">
                          Advanced: {result.advanced.confidence}% confidence
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-300">
                      Provider: {result.provider} • Flags: {result.flags.join(', ') || 'none'}
                    </div>
                    {result.url && <div className="text-xs text-gray-400 mt-1">{result.url}</div>}
                    
                    {/* Advanced Results Display */}
                    {result.advanced && (
                      <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                        <div className="bg-black/20 p-2 rounded">
                          <div className="text-gray-400">Deception</div>
                          <div className="text-white font-mono">{result.advanced.analysis.deception}%</div>
                        </div>
                        <div className="bg-black/20 p-2 rounded">
                          <div className="text-gray-400">Financial Risk</div>
                          <div className="text-white font-mono">{result.advanced.analysis.financialRisk}%</div>
                        </div>
                        <div className="bg-black/20 p-2 rounded">
                          <div className="text-gray-400">Urgency</div>
                          <div className="text-white font-mono">{result.advanced.analysis.urgency}%</div>
                        </div>
                        <div className="bg-black/20 p-2 rounded">
                          <div className="text-gray-400">Patterns</div>
                          <div className="text-white font-mono">{result.advanced.detectedPatterns.length}</div>
                        </div>
                      </div>
                    )}
                    
                    {result.advanced?.urlIntelligence && (
                      <div className="mt-2 text-xs">
                        <span className="text-gray-400">Domain:</span>
                        <span className="text-white ml-2">{result.advanced.urlIntelligence.domain}</span>
                        <span className={`ml-2 px-1 py-0.5 rounded text-xs ${
                          result.advanced.urlIntelligence.reputation === 'malicious' ? 'bg-red-600 text-white' :
                          result.advanced.urlIntelligence.reputation === 'suspicious' ? 'bg-orange-600 text-white' :
                          'bg-gray-600 text-white'
                        }`}>
                          {result.advanced.urlIntelligence.reputation}
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="text-xs text-gray-400">#{i + 1}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
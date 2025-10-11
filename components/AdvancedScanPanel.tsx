'use client'
import { useState } from 'react'

interface AdvancedScanResult {
  id: string
  risk: {
    score: number
    level: string
    factors: Array<{ name: string; value: number; weight: number }>
  }
  aiAnalysis: {
    confidence: number
    threatLevel: string
    flags: string[]
    analysis: {
      sentiment: number
      urgency: number
      deception: number
      financialRisk: number
    }
  }
  urlIntelligence?: {
    domain: string
    reputation: string
    riskScore: number
    threatCategories: string[]
  }
  recommendations: string[]
}

export default function AdvancedScanPanel() {
  const [inputType, setInputType] = useState<'text'|'url'>('text')
  const [content, setContent] = useState('')
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AdvancedScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [capabilities, setCapabilities] = useState<any>(null)

  const loadCapabilities = async () => {
    try {
      const res = await fetch('/api/advanced-scan')
      const data = await res.json()
      if (data.ok) setCapabilities(data)
    } catch (e) {
      console.error('Failed to load capabilities:', e)
    }
  }

  const performAdvancedScan = async () => {
    if (!content.trim() && !url.trim()) return
    
    setLoading(true)
    setError(null)
    setResult(null)
    
    try {
      const res = await fetch('/api/advanced-scan', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          inputType,
          content: inputType === 'text' ? content : undefined,
          url: inputType === 'url' ? url : undefined,
          deepScan: true,
          includeURLAnalysis: true
        })
      })
      
      const data = await res.json()
      if (data.ok) {
        setResult(data.data)
      } else {
        setError(data.error || 'Advanced scan failed')
      }
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gradient-to-br from-purple-900/20 to-blue-900/20 backdrop-blur-sm rounded-lg p-6 border border-purple-500/30">
      <div className="flex items-center gap-2 mb-4">
        <div className="text-2xl">🔒</div>
        <h2 className="text-xl font-semibold text-white">Advanced Security Scanner</h2>
        <button 
          onClick={loadCapabilities}
          className="ml-auto text-xs px-2 py-1 rounded bg-purple-600/50 hover:bg-purple-600/70 text-white"
        >
          Check Capabilities
        </button>
      </div>
      
      {capabilities && (
        <div className="mb-4 p-3 rounded bg-black/20 text-xs">
          <div className="text-green-400 mb-2">🤖 AI Providers: {Object.entries(capabilities.capabilities.providers).filter(([_, active]) => active).map(([name]) => name).join(', ') || 'None'}</div>
          <div className="text-blue-400">⚡ Features: Multi-layer AI • URL Intelligence • Threat DB • Social Engineering Detection</div>
        </div>
      )}
      
      <div className="space-y-4">
        {/* Input Type Selection */}
        <div className="flex gap-2">
          <button 
            onClick={() => setInputType('text')} 
            className={`px-3 py-2 rounded font-medium ${inputType === 'text' ? 'bg-purple-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
          >
            🔤 Text Analysis
          </button>
          <button 
            onClick={() => setInputType('url')} 
            className={`px-3 py-2 rounded font-medium ${inputType === 'url' ? 'bg-purple-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
          >
            🌐 URL Intelligence
          </button>
        </div>
        
        {/* Input Area */}
        {inputType === 'text' ? (
          <textarea 
            value={content} 
            onChange={e => setContent(e.target.value)}
            maxLength={5000}
            className="w-full h-32 p-3 rounded bg-black/30 border border-gray-600 text-white placeholder-gray-400 focus:border-purple-500 focus:outline-none"
            placeholder="Paste suspicious text, email, or message content for advanced threat analysis..."
          />
        ) : (
          <input 
            value={url} 
            onChange={e => setUrl(e.target.value)}
            className="w-full p-3 rounded bg-black/30 border border-gray-600 text-white placeholder-gray-400 focus:border-purple-500 focus:outline-none"
            placeholder="https://suspicious-url.com"
          />
        )}
        
        {/* Scan Button */}
        <button 
          disabled={loading || (!content.trim() && !url.trim())}
          onClick={performAdvancedScan}
          className="w-full px-4 py-3 rounded bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
              Advanced Scanning...
            </>
          ) : (
            <>
              🔍 Run Advanced Security Scan
            </>
          )}
        </button>
        
        {/* Error Display */}
        {error && (
          <div className="p-3 rounded bg-red-900/30 border border-red-500/50 text-red-200">
            <div className="font-medium">⚠️ Scan Failed</div>
            <div className="text-sm mt-1">{error}</div>
          </div>
        )}
        
        {/* Advanced Results */}
        {result && (
          <div className="space-y-4 mt-6">
            {/* Risk Score */}
            <div className={`p-4 rounded border-2 ${
              result.risk.level === 'critical' ? 'bg-red-900/30 border-red-500' :
              result.risk.level === 'high' ? 'bg-orange-900/30 border-orange-500' :
              result.risk.level === 'medium' ? 'bg-yellow-900/30 border-yellow-500' :
              'bg-green-900/30 border-green-500'
            }`}>
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-white">🎯 Threat Assessment</span>
                <span className={`px-2 py-1 rounded text-sm font-bold ${
                  result.risk.level === 'critical' ? 'bg-red-600 text-white' :
                  result.risk.level === 'high' ? 'bg-orange-600 text-white' :
                  result.risk.level === 'medium' ? 'bg-yellow-600 text-black' :
                  'bg-green-600 text-white'
                }`}>
                  {result.risk.level.toUpperCase()} ({result.risk.score}%)
                </span>
              </div>
              
              {/* Risk Factors */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                {result.risk.factors.map((factor, i) => (
                  <div key={i} className="flex justify-between">
                    <span className="text-gray-300">{factor.name}:</span>
                    <span className="text-white font-mono">{Math.round(factor.value)}%</span>
                  </div>
                ))}
              </div>
            </div>
            
            {/* AI Analysis */}
            <div className="p-4 rounded bg-blue-900/20 border border-blue-500/30">
              <div className="font-semibold text-white mb-2">🤖 AI Analysis ({result.aiAnalysis.confidence}% confidence)</div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-gray-300">Deception Level:</div>
                  <div className="text-white font-mono">{result.aiAnalysis.analysis.deception}%</div>
                </div>
                <div>
                  <div className="text-gray-300">Financial Risk:</div>
                  <div className="text-white font-mono">{result.aiAnalysis.analysis.financialRisk}%</div>
                </div>
                <div>
                  <div className="text-gray-300">Urgency Tactics:</div>
                  <div className="text-white font-mono">{result.aiAnalysis.analysis.urgency}%</div>
                </div>
                <div>
                  <div className="text-gray-300">Threat Flags:</div>
                  <div className="text-white font-mono">{result.aiAnalysis.flags.length}</div>
                </div>
              </div>
              
              {result.aiAnalysis.flags.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {result.aiAnalysis.flags.map((flag, i) => (
                    <span key={i} className="px-2 py-1 rounded text-xs bg-red-600/30 text-red-200">
                      {flag}
                    </span>
                  ))}
                </div>
              )}
            </div>
            
            {/* URL Intelligence */}
            {result.urlIntelligence && (
              <div className="p-4 rounded bg-indigo-900/20 border border-indigo-500/30">
                <div className="font-semibold text-white mb-2">🌐 URL Intelligence</div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-300">Domain:</span>
                    <span className="text-white font-mono">{result.urlIntelligence.domain}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Reputation:</span>
                    <span className={`font-semibold ${
                      result.urlIntelligence.reputation === 'malicious' ? 'text-red-400' :
                      result.urlIntelligence.reputation === 'suspicious' ? 'text-orange-400' :
                      result.urlIntelligence.reputation === 'trusted' ? 'text-green-400' :
                      'text-gray-400'
                    }`}>
                      {result.urlIntelligence.reputation}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {result.urlIntelligence.threatCategories.map((category, i) => (
                      <span key={i} className="px-2 py-1 rounded text-xs bg-purple-600/30 text-purple-200">
                        {category}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}
            
            {/* Recommendations */}
            <div className="p-4 rounded bg-green-900/20 border border-green-500/30">
              <div className="font-semibold text-white mb-2">💡 Security Recommendations</div>
              <ul className="space-y-1 text-sm">
                {result.recommendations.map((rec, i) => (
                  <li key={i} className="text-gray-200">{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
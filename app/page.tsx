'use client'
import { useState } from 'react'
import AnalyzeForm from '../components/AnalyzeForm'
import BatchUploader from '../components/BatchUploader'
import { ExportButtons } from '../components/ExportButtons'

interface AnalysisResult {
  id: string
  risk: { score: number; level: string; reasons: string[] }
  provider: string
  flags: string[]
  url?: string
}

export default function HomePage() {
  const [results, setResults] = useState<AnalysisResult[]>([])
  const [scanUrl, setScanUrl] = useState('')
  const [scanLoading, setScanLoading] = useState(false)
  const [scanResult, setScanResult] = useState<any>(null)
  const [analytics, setAnalytics] = useState<any>(null)

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
      {/* Analytics Panel */}
      <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-white">📊 Statistici</h2>
          <button onClick={loadAnalytics} className="btn-secondary text-sm">Actualizează</button>
        </div>
        {analytics && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="bg-blue-500/20 p-4 rounded">
              <div className="text-2xl font-bold text-blue-300">{analytics.totalAnalyses}</div>
              <div className="text-sm text-gray-300">Analize totale</div>
            </div>
            <div className="bg-red-500/20 p-4 rounded">
              <div className="text-2xl font-bold text-red-300">{analytics.distribution.high}</div>
              <div className="text-sm text-gray-300">Risc ridicat</div>
            </div>
            <div className="bg-yellow-500/20 p-4 rounded">
              <div className="text-2xl font-bold text-yellow-300">{analytics.distribution.medium}</div>
              <div className="text-sm text-gray-300">Risc mediu</div>
            </div>
            <div className="bg-green-500/20 p-4 rounded">
              <div className="text-2xl font-bold text-green-300">{analytics.distribution.low}</div>
              <div className="text-sm text-gray-300">Risc scăzut</div>
            </div>
          </div>
        )}
      </div>

      {/* Main Analysis */}
      <div className="grid md:grid-cols-2 gap-8">
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">🔍 Analiză individuală</h2>
          <AnalyzeForm onResult={handleAnalyzeResult} />
        </div>

        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">🌐 Scan VirusTotal</h2>
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
              {scanLoading ? 'Scanez...' : 'Scanează cu VirusTotal'}
            </button>
            {scanResult && (
              <div className={`p-3 rounded ${scanResult.verdict === 'malicious' ? 'bg-red-500/20 text-red-300' : 'bg-green-500/20 text-green-300'}`}>
                <strong>Verdict:</strong> {scanResult.verdict}
                <br />
                <strong>Risc:</strong> {scanResult.risk.level} ({scanResult.risk.score}%)
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Batch Upload */}
      <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">📋 Procesare în lot</h2>
        <BatchUploader onBatch={handleBatchResults} />
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-white">📋 Rezultate ({results.length})</h2>
            <ExportButtons data={results} />
          </div>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {results.map((result, i) => (
              <div key={result.id} className={`p-4 rounded border ${
                result.risk.level === 'high' ? 'bg-red-500/20 border-red-500' :
                result.risk.level === 'medium' ? 'bg-yellow-500/20 border-yellow-500' :
                'bg-green-500/20 border-green-500'
              }`}>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="font-medium text-white">
                      Risc {result.risk.level} ({result.risk.score}%)
                    </div>
                    <div className="text-sm text-gray-300">
                      Provider: {result.provider} • Flags: {result.flags.join(', ') || 'none'}
                    </div>
                    {result.url && <div className="text-xs text-gray-400 mt-1">{result.url}</div>}
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
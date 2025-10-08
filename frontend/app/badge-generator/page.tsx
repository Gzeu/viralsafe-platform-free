'use client'

import { useState, useEffect } from 'react'
import { Shield, Copy, Eye, Download, Code, Globe } from 'lucide-react'

interface BadgeStyle {
  name: string
  description: string
  preview: string
  recommended?: boolean
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function BadgeGenerator() {
  const [domain, setDomain] = useState('')
  const [selectedStyle, setSelectedStyle] = useState('modern')
  const [selectedFormat, setSelectedFormat] = useState('html')
  const [embedCode, setEmbedCode] = useState('')
  const [widgetCode, setWidgetCode] = useState('')
  const [badgeStyles, setBadgeStyles] = useState<BadgeStyle[]>([])
  const [verification, setVerification] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState('')

  useEffect(() => {
    loadBadgeStyles()
  }, [])

  const loadBadgeStyles = async () => {
    try {
      const response = await fetch(`${API_URL}/badge/styles`)
      if (response.ok) {
        const data = await response.json()
        setBadgeStyles(data.styles)
      }
    } catch (err) {
      console.error('Failed to load badge styles:', err)
    }
  }

  const generateBadge = async () => {
    if (!domain.trim()) return
    
    setLoading(true)
    
    try {
      // Get verification status
      const verifyResponse = await fetch(`${API_URL}/verify/${domain}`)
      if (verifyResponse.ok) {
        const verifyData = await verifyResponse.json()
        setVerification(verifyData)
      }
      
      // Get embed code
      const embedResponse = await fetch(`${API_URL}/badge/embed/${domain}?style=${selectedStyle}&format=${selectedFormat}`)
      if (embedResponse.ok) {
        const embedData = await embedResponse.json()
        setEmbedCode(embedData.embed_code)
      }
      
      // Get widget code
      const widgetResponse = await fetch(`${API_URL}/widget/${domain}`)
      if (widgetResponse.ok) {
        const widgetData = await widgetResponse.json()
        setWidgetCode(widgetData.widget_code)
      }
      
    } catch (err) {
      console.error('Badge generation failed:', err)
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text)
    setCopied(type)
    setTimeout(() => setCopied(''), 2000)
  }

  const getBadgePreviewUrl = (style: string) => {
    return `${API_URL}/badge/verified/${domain || 'example.com'}?style=${style}`
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
                <h1 className="text-2xl font-bold text-gray-900">Badge Generator</h1>
                <p className="text-sm text-gray-600">Create verification badges for your website</p>
              </div>
            </div>
            <a 
              href="/" 
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Back to Home
            </a>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Domain Input */}
        <div className="bg-white rounded-xl shadow-lg border p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Globe className="w-5 h-5 mr-2 text-blue-600" />
            Enter Your Domain
          </h2>
          
          <div className="flex space-x-4">
            <div className="flex-1">
              <input
                type="text"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                placeholder="example.com"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button
              onClick={generateBadge}
              disabled={loading || !domain.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Shield className="w-4 h-4" />
              )}
              <span>Generate Badge</span>
            </button>
          </div>
        </div>

        {/* Verification Status */}
        {verification && (
          <div className={`bg-white rounded-xl shadow-lg border-2 p-6 mb-8 ${
            verification.verified ? 'border-green-200 bg-green-50' : 'border-yellow-200 bg-yellow-50'
          }`}>
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              {verification.verified ? (
                <Shield className="w-5 h-5 text-green-600 mr-2" />
              ) : (
                <Shield className="w-5 h-5 text-yellow-600 mr-2" />
              )}
              Verification Status for {verification.domain}
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-white rounded-lg border">
                <div className={`text-2xl font-bold ${
                  verification.verified ? 'text-green-600' : 'text-yellow-600'
                }`}>
                  {(verification.safety_score * 100).toFixed(0)}%
                </div>
                <div className="text-sm text-gray-600">Safety Score</div>
              </div>
              
              <div className="text-center p-4 bg-white rounded-lg border">
                <div className={`text-sm font-medium uppercase ${
                  verification.risk_level === 'low' ? 'text-green-600' :
                  verification.risk_level === 'medium' ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {verification.risk_level} Risk
                </div>
                <div className="text-sm text-gray-600">Risk Level</div>
              </div>
              
              <div className="text-center p-4 bg-white rounded-lg border">
                <div className="text-lg font-medium">
                  {verification.sources_checked}
                </div>
                <div className="text-sm text-gray-600">Sources Checked</div>
              </div>
            </div>
            
            {verification.summary && (
              <div className="mt-4 p-3 bg-white rounded border text-sm">
                {verification.summary}
              </div>
            )}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Badge Styles */}
          <div className="bg-white rounded-xl shadow-lg border p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Eye className="w-5 h-5 mr-2 text-blue-600" />
              Badge Styles
            </h3>
            
            <div className="space-y-4">
              {badgeStyles.map((style) => (
                <div 
                  key={style.name}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all hover:shadow-md ${
                    selectedStyle === style.name ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                  }`}
                  onClick={() => setSelectedStyle(style.name)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-medium capitalize">{style.name}</h4>
                      {style.recommended && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                          Recommended
                        </span>
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{style.description}</p>
                  
                  {domain && (
                    <div className="flex justify-center p-4 bg-gray-50 rounded">
                      <img 
                        src={getBadgePreviewUrl(style.name)}
                        alt={`${style.name} badge preview`}
                        className="max-h-12"
                        onError={(e) => {
                          (e.target as HTMLImageElement).style.display = 'none'
                        }}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Code Generation */}
          <div className="space-y-6">
            {/* Embed Code */}
            <div className="bg-white rounded-xl shadow-lg border p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Code className="w-5 h-5 mr-2 text-blue-600" />
                Embed Code
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Format
                  </label>
                  <select
                    value={selectedFormat}
                    onChange={(e) => setSelectedFormat(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="html">HTML</option>
                    <option value="markdown">Markdown</option>
                    <option value="bbcode">BBCode</option>
                  </select>
                </div>
                
                {embedCode && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium text-gray-700">Code</label>
                      <button
                        onClick={() => copyToClipboard(embedCode, 'embed')}
                        className="flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-700"
                      >
                        <Copy className="w-4 h-4" />
                        <span>{copied === 'embed' ? 'Copied!' : 'Copy'}</span>
                      </button>
                    </div>
                    <textarea
                      value={embedCode}
                      readOnly
                      className="w-full h-24 p-3 bg-gray-50 border border-gray-300 rounded-lg text-sm font-mono"
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Widget Code */}
            {widgetCode && (
              <div className="bg-white rounded-xl shadow-lg border p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <Download className="w-5 h-5 mr-2 text-blue-600" />
                  JavaScript Widget
                </h3>
                
                <div className="space-y-4">
                  <p className="text-sm text-gray-600">
                    Add this widget to show a floating verification badge on your site.
                  </p>
                  
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium text-gray-700">Widget Code</label>
                      <button
                        onClick={() => copyToClipboard(widgetCode, 'widget')}
                        className="flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-700"
                      >
                        <Copy className="w-4 h-4" />
                        <span>{copied === 'widget' ? 'Copied!' : 'Copy'}</span>
                      </button>
                    </div>
                    <textarea
                      value={widgetCode}
                      readOnly
                      className="w-full h-32 p-3 bg-gray-50 border border-gray-300 rounded-lg text-sm font-mono"
                    />
                  </div>
                  
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">Integration Steps:</h4>
                    <ol className="list-decimal list-inside text-sm text-blue-800 space-y-1">
                      <li>Copy the widget code above</li>
                      <li>Paste it before the closing &lt;/body&gt; tag on your website</li>
                      <li>The widget will automatically verify your domain and display status</li>
                    </ol>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Usage Examples */}
        {domain && embedCode && (
          <div className="bg-white rounded-xl shadow-lg border p-6 mt-8">
            <h3 className="text-lg font-semibold mb-4">Live Preview</h3>
            
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <p className="text-gray-600 mb-4">Your badge will look like this:</p>
              <img 
                src={getBadgePreviewUrl(selectedStyle)}
                alt="Badge preview"
                className="inline-block"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjQwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iNDAiIGZpbGw9IiNlNWU3ZWIiLz48dGV4dCB4PSIxMDAiIHk9IjI1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM2YjczODAiPlByZXZpZXcgTm90IEF2YWlsYWJsZTwvdGV4dD48L3N2Zz4='
                }}
              />
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-500 space-y-2">
          <p className="text-sm">
            🛡️ ViralSafe Badge Generator • Open Source • Free Tier
          </p>
          <p className="text-xs">
            Enhance your website's credibility with verification badges
          </p>
        </footer>
      </div>
    </main>
  )
}
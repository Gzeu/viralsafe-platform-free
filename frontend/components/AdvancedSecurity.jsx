"use client";

import { useState, useEffect } from 'react';
import { Shield, Zap, Brain, TrendingUp, AlertTriangle, CheckCircle, XCircle, Clock, Globe } from 'lucide-react';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://viralsafe-platform-free-api.onrender.com'
  : 'http://localhost:10000';

const AdvancedSecurity = () => {
  const [url, setUrl] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [error, setError] = useState('');
  const [systemStatus, setSystemStatus] = useState(null);
  const [analytics, setAnalytics] = useState(null);

  // Load system status and analytics on component mount
  useEffect(() => {
    loadSystemData();
  }, []);

  const loadSystemData = async () => {
    try {
      // Load system status
      const statusResponse = await fetch(`${API_BASE_URL}/api/system-status`);
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setSystemStatus(statusData);
      }

      // Load analytics
      const analyticsResponse = await fetch(`${API_BASE_URL}/api/analytics`);
      if (analyticsResponse.ok) {
        const analyticsData = await analyticsResponse.json();
        setAnalytics(analyticsData);
      }
    } catch (error) {
      console.warn('Failed to load system data:', error);
    }
  };

  const handleAdvancedScan = async () => {
    if (!url.trim()) {
      setError('Please enter a valid URL');
      return;
    }

    // Basic URL validation
    try {
      new URL(url);
    } catch {
      setError('Please enter a valid URL (including https:// or http://)');
      return;
    }

    setIsScanning(true);
    setError('');
    setScanResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/advanced-scan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          url: url.trim(),
          deep_scan: true // Enable deep scanning for enhanced analysis
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const result = await response.json();
      setScanResult(result);
      
      // Refresh analytics after successful scan
      loadSystemData();
      
    } catch (error) {
      console.error('Advanced scan failed:', error);
      setError(`Scan failed: ${error.message}`);
    } finally {
      setIsScanning(false);
    }
  };

  const getTrustScoreBadge = (score) => {
    if (score >= 90) return { color: 'bg-green-500', text: 'Excellent', icon: CheckCircle };
    if (score >= 75) return { color: 'bg-blue-500', text: 'Good', icon: CheckCircle };
    if (score >= 50) return { color: 'bg-yellow-500', text: 'Caution', icon: AlertTriangle };
    return { color: 'bg-red-500', text: 'High Risk', icon: XCircle };
  };

  const getThreatLevelBadge = (level) => {
    if (level <= 3) return { color: 'bg-green-500', text: 'Low' };
    if (level <= 6) return { color: 'bg-yellow-500', text: 'Medium' };
    return { color: 'bg-red-500', text: 'High' };
  };

  const formatScanTime = (timeMs) => {
    if (timeMs < 1000) return `${timeMs}ms`;
    return `${(timeMs / 1000).toFixed(1)}s`;
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <div className="p-3 bg-gradient-to-r from-purple-500 to-blue-600 rounded-full">
            <Brain className="h-8 w-8 text-white" />
          </div>
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          AI-Powered Security Analysis
        </h2>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Advanced threat detection using multiple AI providers and comprehensive security scanning
        </p>
      </div>

      {/* System Status Overview */}
      {systemStatus && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 text-blue-500 mr-2" />
            System Status
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {systemStatus.features?.ai_analysis ? 'AI' : 'Basic'}
              </div>
              <div className="text-sm text-gray-500">Analysis Mode</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {systemStatus.database?.collections?.advanced_scans || 0}
              </div>
              <div className="text-sm text-gray-500">Scans Today</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {systemStatus.uptime?.formatted || '0s'}
              </div>
              <div className="text-sm text-gray-500">Uptime</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-600">v3.1</div>
              <div className="text-sm text-gray-500">Version</div>
            </div>
          </div>
        </div>
      )}

      {/* Scan Interface */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Shield className="h-5 w-5 text-green-500 mr-2" />
          Advanced URL Security Scan
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Website URL to Analyze
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              disabled={isScanning}
            />
          </div>
          
          <button
            onClick={handleAdvancedScan}
            disabled={isScanning || !url.trim()}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-md hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center space-x-2"
          >
            {isScanning ? (
              <>
                <Clock className="h-5 w-5 animate-spin" />
                <span>Analyzing Security...</span>
              </>
            ) : (
              <>
                <Zap className="h-5 w-5" />
                <span>Run Advanced Scan</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <XCircle className="h-5 w-5 text-red-500 mr-2" />
            <span className="text-red-700 font-medium">Error</span>
          </div>
          <p className="text-red-600 mt-1">{error}</p>
        </div>
      )}

      {/* Scan Results */}
      {scanResult && (
        <div className="space-y-6">
          {/* Main Results Card */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900">Security Analysis Results</h3>
              <div className="flex items-center space-x-2">
                <Globe className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-500">
                  Scanned in {formatScanTime(scanResult.scan_time)}
                </span>
              </div>
            </div>

            {/* Trust Score */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="text-center">
                <div className={`inline-flex items-center px-4 py-2 rounded-full text-white font-semibold ${getTrustScoreBadge(scanResult.trust_score).color}`}>
                  {React.createElement(getTrustScoreBadge(scanResult.trust_score).icon, { className: "h-4 w-4 mr-1" })}
                  {scanResult.trust_score}% Trust Score
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {getTrustScoreBadge(scanResult.trust_score).text}
                </div>
              </div>
              
              <div className="text-center">
                <div className={`inline-flex items-center px-4 py-2 rounded-full text-white font-semibold ${getThreatLevelBadge(scanResult.threat_level).color}`}>
                  {scanResult.threat_level}/10 Threat Level
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {getThreatLevelBadge(scanResult.threat_level).text} Risk
                </div>
              </div>
              
              <div className="text-center">
                <div className="inline-flex items-center px-4 py-2 rounded-full bg-blue-500 text-white font-semibold">
                  <Brain className="h-4 w-4 mr-1" />
                  {scanResult.ai_confidence}% AI Confidence
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {scanResult.ai_provider === 'groq' ? 'AI Enhanced' : 'Fallback Mode'}
                </div>
              </div>
            </div>

            {/* AI Insights */}
            {scanResult.ai_insights && (
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 mb-6">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <Brain className="h-4 w-4 text-blue-500 mr-2" />
                  AI Security Insights
                </h4>
                <p className="text-gray-700">{scanResult.ai_insights}</p>
              </div>
            )}

            {/* Categories & Risk Factors */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Content Categories</h4>
                <div className="space-y-2">
                  {scanResult.categories?.map((category, index) => (
                    <div key={index} className="flex items-center">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                      <span className="text-gray-700 capitalize">{category.replace('_', ' ')}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Risk Factors</h4>
                <div className="space-y-2">
                  {scanResult.risk_factors?.map((factor, index) => (
                    <div key={index} className="flex items-center">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                      <span className="text-gray-700 text-sm">{factor}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Recommendations */}
            {scanResult.recommendations && scanResult.recommendations.length > 0 && (
              <div className="mt-6">
                <h4 className="font-semibold text-gray-900 mb-3">Security Recommendations</h4>
                <div className="space-y-2">
                  {scanResult.recommendations.map((recommendation, index) => (
                    <div key={index} className="flex items-start">
                      <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700 text-sm">{recommendation}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Technical Details */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-3">Technical Details</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Status Code:</span>
                  <span className="ml-1 font-medium">{scanResult.status_code || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-gray-500">Scan Type:</span>
                  <span className="ml-1 font-medium capitalize">{scanResult.scan_type || 'Advanced'}</span>
                </div>
                <div>
                  <span className="text-gray-500">Version:</span>
                  <span className="ml-1 font-medium">{scanResult.version || '3.1.0'}</span>
                </div>
                <div>
                  <span className="text-gray-500">Provider:</span>
                  <span className="ml-1 font-medium capitalize">{scanResult.ai_provider || 'AI'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Analytics Summary */}
      {analytics && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 text-purple-500 mr-2" />
            Platform Analytics
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {analytics.usage_statistics?.total_all_scans || 0}
              </div>
              <div className="text-sm text-gray-500">Total Scans</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {analytics.usage_statistics?.total_advanced_scans || 0}
              </div>
              <div className="text-sm text-gray-500">Advanced Scans</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {analytics.activity?.today?.total || 0}
              </div>
              <div className="text-sm text-gray-500">Today</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-600">
                {analytics.features_status?.ai_analysis ? 'AI' : 'Basic'}
              </div>
              <div className="text-sm text-gray-500">Mode</div>
            </div>
          </div>
        </div>
      )}

      {/* Feature Showcase */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Enhanced v3.1 Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="flex items-center space-x-3">
            <Brain className="h-6 w-6 text-blue-500" />
            <div>
              <div className="font-medium text-gray-900">Multi-AI Analysis</div>
              <div className="text-sm text-gray-600">Groq, Anthropic, OpenAI</div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Shield className="h-6 w-6 text-green-500" />
            <div>
              <div className="font-medium text-gray-900">9-Layer Scanning</div>
              <div className="text-sm text-gray-600">Comprehensive analysis</div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Zap className="h-6 w-6 text-yellow-500" />
            <div>
              <div className="font-medium text-gray-900">Ultra-Fast</div>
              <div className="text-sm text-gray-600">&lt;2s scan time</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedSecurity;
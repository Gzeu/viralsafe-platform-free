"use client";

import { useState, useEffect } from 'react';
import { Shield, Brain, Zap, AlertTriangle, CheckCircle, TrendingUp, Clock, Globe, Activity } from 'lucide-react';
import { apiCall, API_CONFIG, checkBackendHealth, getBackendVersion } from '../config/api';

const AdvancedSecurity = () => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [url, setUrl] = useState('');
  const [analytics, setAnalytics] = useState(null);
  const [apiVersion, setApiVersion] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [error, setError] = useState(null);

  // Load initial data on component mount
  useEffect(() => {
    loadInitialData();
    // Refresh data every 30 seconds
    const interval = setInterval(loadInitialData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadInitialData = async () => {
    try {
      // Load version info
      const version = await getBackendVersion();
      if (version) {
        setApiVersion(version);
      }
      
      // Load system health
      const health = await checkBackendHealth();
      if (health) {
        setSystemHealth(health);
      }
      
      // Load analytics
      const analyticsData = await apiCall(API_CONFIG.ENDPOINTS.analytics);
      if (analyticsData) {
        setAnalytics(analyticsData);
      }
      
    } catch (error) {
      console.warn('Could not load initial data:', error);
    }
  };

  const runAdvancedScan = async () => {
    if (!url.trim()) {
      setError('Please enter a valid URL');
      return;
    }

    // Basic URL validation
    try {
      new URL(url.trim());
    } catch {
      setError('Please enter a valid URL (including https:// or http://)');
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysis(null);
    
    try {
      const result = await apiCall(
        API_CONFIG.ENDPOINTS.advancedScan, 
        'POST', 
        { url: url.trim(), deep_scan: true }
      );
      
      setAnalysis(result);
      
      // Reload analytics after successful scan
      setTimeout(loadInitialData, 1000);
      
    } catch (error) {
      console.error('Advanced scan failed:', error);
      setError(`Scan failed: ${error.message}`);
      
      // Show fallback demo data if API fails
      setAnalysis({
        url: url.trim(),
        trust_score: 75,
        threat_level: 3,
        ai_confidence: 80,
        ai_insights: "Enhanced AI analysis temporarily unavailable. Using fallback security assessment.",
        recommendations: [
          "Verify SSL certificate manually",
          "Check domain reputation with additional tools",
          "Try again in a few moments for full AI analysis"
        ],
        scan_time: 500,
        categories: ["Web Content", "Requires Enhanced Analysis"],
        risk_factors: ["AI analysis service temporarily unavailable"],
        fallback_mode: true,
        ai_provider: "fallback",
        enhanced_mode: false
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !loading && url.trim()) {
      runAdvancedScan();
    }
  };

  const formatScanTime = (timeMs) => {
    if (timeMs < 1000) return `${timeMs}ms`;
    return `${(timeMs / 1000).toFixed(1)}s`;
  };

  return (
    <div className="space-y-8">
      {/* Header with Version Info */}
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <div className="p-4 bg-gradient-to-br from-purple-500 via-indigo-600 to-blue-600 rounded-full shadow-lg">
            <Brain className="h-10 w-10 text-white" />
          </div>
        </div>
        <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 bg-clip-text text-transparent mb-3">
          AI-Powered Security Analysis
        </h2>
        <p className="text-gray-600 text-lg max-w-2xl mx-auto">
          Advanced threat detection using multiple AI providers and comprehensive security scanning
          {apiVersion && (
            <span className="ml-2 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
              v{apiVersion.version} 
              {apiVersion.environment?.groq_configured && ' 🤖'}
            </span>
          )}
        </p>
      </div>

      {/* System Status Overview */}
      {(systemHealth || apiVersion) && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="h-5 w-5 text-blue-500 mr-2" />
            System Status
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {apiVersion?.environment?.groq_configured ? 'AI Enhanced' : 'Basic'}
              </div>
              <div className="text-sm text-gray-500">Analysis Mode</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {analytics?.usage_statistics?.total_advanced_scans || 0}
              </div>
              <div className="text-sm text-gray-500">Advanced Scans</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {systemHealth?.uptime?.formatted || apiVersion?.deployment_time || 'Live'}
              </div>
              <div className="text-sm text-gray-500">Uptime</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-600">
                {apiVersion?.version || '3.1'}
              </div>
              <div className="text-sm text-gray-500">Version</div>
            </div>
          </div>
        </div>
      )}

      {/* Scan Interface */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Shield className="h-5 w-5 text-green-500 mr-2" />
          Advanced URL Security Scan
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Website URL to Analyze
            </label>
            <div className="flex gap-3">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="https://example.com"
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                disabled={loading}
              />
              <button
                onClick={runAdvancedScan}
                disabled={loading || !url.trim()}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-2 font-medium"
              >
                {loading ? (
                  <>
                    <Clock className="h-5 w-5 animate-spin" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Zap className="h-5 w-5" />
                    <span>Advanced Scan</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
            <span className="text-red-700 font-medium">Error</span>
          </div>
          <p className="text-red-600 mt-1">{error}</p>
        </div>
      )}

      {/* Scan Results */}
      {analysis && (
        <div className="space-y-6">
          {/* Main Results Card */}
          <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900">Security Analysis Results</h3>
              <div className="flex items-center space-x-4">
                {analysis.fallback_mode && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                    Fallback Mode
                  </span>
                )}
                <div className="flex items-center space-x-2">
                  <Globe className="h-4 w-4 text-gray-500" />
                  <span className="text-sm text-gray-500">
                    Scanned in {formatScanTime(analysis.scan_time)}
                  </span>
                </div>
              </div>
            </div>

            {/* Trust Score Badges */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="text-center">
                <div className={`inline-flex items-center px-4 py-2 rounded-full text-white font-semibold ${
                  analysis.trust_score >= 90 ? 'bg-green-500' :
                  analysis.trust_score >= 75 ? 'bg-blue-500' :
                  analysis.trust_score >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                }`}>
                  {analysis.trust_score >= 90 ? (
                    <CheckCircle className="h-4 w-4 mr-1" />
                  ) : (
                    <Shield className="h-4 w-4 mr-1" />
                  )}
                  {analysis.trust_score}% Trust Score
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {analysis.trust_score >= 90 ? 'Excellent' :
                   analysis.trust_score >= 75 ? 'Good' :
                   analysis.trust_score >= 50 ? 'Caution' : 'High Risk'}
                </div>
              </div>
              
              <div className="text-center">
                <div className={`inline-flex items-center px-4 py-2 rounded-full text-white font-semibold ${
                  analysis.threat_level <= 3 ? 'bg-green-500' :
                  analysis.threat_level <= 6 ? 'bg-yellow-500' : 'bg-red-500'
                }`}>
                  {analysis.threat_level}/10 Threat Level
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {analysis.threat_level <= 3 ? 'Low' :
                   analysis.threat_level <= 6 ? 'Medium' : 'High'} Risk
                </div>
              </div>
              
              <div className="text-center">
                <div className="inline-flex items-center px-4 py-2 rounded-full bg-purple-500 text-white font-semibold">
                  <Brain className="h-4 w-4 mr-1" />
                  {analysis.ai_confidence}% Confidence
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {analysis.ai_provider === 'groq' ? 'AI Enhanced' : 
                   analysis.fallback_mode ? 'Fallback Mode' : 'Analyzed'}
                </div>
              </div>
            </div>

            {/* AI Insights */}
            {analysis.ai_insights && (
              <div className={`rounded-lg p-4 mb-6 ${
                analysis.fallback_mode 
                  ? 'bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200'
                  : 'bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200'
              }`}>
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <Brain className="h-4 w-4 text-blue-500 mr-2" />
                  {analysis.ai_provider === 'groq' ? 'AI Security Insights' : 'Security Analysis'}
                </h4>
                <p className="text-gray-700">{analysis.ai_insights}</p>
              </div>
            )}

            {/* Categories & Risk Factors */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Content Categories</h4>
                <div className="space-y-2">
                  {analysis.categories?.map((category, index) => (
                    <div key={index} className="flex items-center">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                      <span className="text-gray-700 capitalize">{category.replace('_', ' ')}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Risk Assessment</h4>
                <div className="space-y-2">
                  {analysis.risk_factors?.map((factor, index) => (
                    <div key={index} className="flex items-center">
                      <div className={`w-2 h-2 rounded-full mr-2 ${
                        factor.includes('None detected') || factor.includes('Analysis completed') 
                          ? 'bg-green-500' : 'bg-yellow-500'
                      }`}></div>
                      <span className="text-gray-700 text-sm">{factor}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Recommendations */}
            {analysis.recommendations && analysis.recommendations.length > 0 && (
              <div className="mt-6">
                <h4 className="font-semibold text-gray-900 mb-3">Security Recommendations</h4>
                <div className="space-y-2">
                  {analysis.recommendations.map((recommendation, index) => (
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
                  <span className="ml-1 font-medium">{analysis.status_code || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-gray-500">Scan Type:</span>
                  <span className="ml-1 font-medium capitalize">{analysis.scan_type || 'Advanced'}</span>
                </div>
                <div>
                  <span className="text-gray-500">Version:</span>
                  <span className="ml-1 font-medium">{analysis.version || apiVersion?.version || '3.1.0'}</span>
                </div>
                <div>
                  <span className="text-gray-500">Provider:</span>
                  <span className="ml-1 font-medium capitalize">{analysis.ai_provider || 'Analysis'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Analytics Summary */}
      {analytics && !analysis && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 text-purple-500 mr-2" />
            Platform Analytics
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {analytics.usage_statistics?.total_all_scans || analytics.total_analyses || 0}
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
                {apiVersion?.environment?.groq_configured ? 'AI' : 'Basic'}
              </div>
              <div className="text-sm text-gray-500">Mode</div>
            </div>
          </div>
        </div>
      )}

      {/* Feature Showcase */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Enhanced v3.1 Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="flex items-center space-x-3">
            <Brain className="h-6 w-6 text-blue-500" />
            <div>
              <div className="font-medium text-gray-900">Multi-AI Analysis</div>
              <div className="text-sm text-gray-600">
                {apiVersion?.environment?.groq_configured ? 'Groq AI Active 🤖' : 'Fallback Mode 📊'}
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Shield className="h-6 w-6 text-green-500" />
            <div>
              <div className="font-medium text-gray-900">Advanced Scanning</div>
              <div className="text-sm text-gray-600">9-layer security analysis</div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Zap className="h-6 w-6 text-yellow-500" />
            <div>
              <div className="font-medium text-gray-900">Ultra-Fast</div>
              <div className="text-sm text-gray-600">&lt;2s comprehensive scans</div>
            </div>
          </div>
        </div>
        
        {/* Backend Connection Status */}
        <div className="mt-4 pt-4 border-t border-blue-200">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Backend Connection:</span>
            <span className={`font-medium ${
              apiVersion ? 'text-green-600' : 'text-yellow-600'
            }`}>
              {apiVersion ? `✅ Connected to v${apiVersion.version}` : '⚠️ Connecting...'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedSecurity;
// Frontend API Configuration for ViralSafe v3.1 Enhanced
// Centralized API management with environment detection

export const API_CONFIG = {
  BASE_URL: process.env.NODE_ENV === 'production' 
    ? 'https://viralsafe-platform-free-api.onrender.com'
    : 'http://localhost:10000',
  
  ENDPOINTS: {
    health: '/health',
    analyze: '/api/analyze', 
    advancedScan: '/api/advanced-scan',  // NEW v3.1
    systemStatus: '/api/system-status',   // NEW v3.1
    analytics: '/api/analytics',
    version: '/api/version'               // NEW v3.1
  }
}

export const apiCall = async (endpoint, method = 'GET', body = null) => {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`
  
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  }
  
  if (body) {
    options.body = JSON.stringify(body)
  }
  
  try {
    const response = await fetch(url, options)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error(`API call failed for ${endpoint}:`, error)
    throw error
  }
}

// Utility functions for API integration
export const checkBackendHealth = async () => {
  try {
    const health = await apiCall(API_CONFIG.ENDPOINTS.health)
    return health
  } catch (error) {
    console.warn('Backend health check failed:', error)
    return null
  }
}

export const getBackendVersion = async () => {
  try {
    const version = await apiCall(API_CONFIG.ENDPOINTS.version)
    return version
  } catch (error) {
    console.warn('Could not fetch backend version:', error)
    return null
  }
}

export default API_CONFIG
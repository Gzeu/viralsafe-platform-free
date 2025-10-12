import { advancedClassifyText } from './ai-advanced'
import { URLIntelligenceAnalyzer } from './url-intelligence'

// Backward compatible interface
export type AIResult = { aiScore: number; flags: string[]; provider: string }

// Enhanced result interface for advanced features
export interface EnhancedAIResult extends AIResult {
  confidence: number
  threatLevel: 'low' | 'medium' | 'high' | 'critical'
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

// Main classification function with fallback
export async function classifyText(text: string, useAdvanced: boolean = true): Promise<AIResult | EnhancedAIResult> {
  try {
    if (useAdvanced && (process.env.OPENAI_API_KEY || process.env.GROQ_API_KEY || process.env.GEMINI_API_KEY)) {
      const result = await advancedClassifyText(text)
      
      // If text contains URLs, analyze them too
      const urlRegex = /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/g
      const urls = text.match(urlRegex)
      
      if (urls && urls.length > 0) {
        try {
          const urlAnalysis = await URLIntelligenceAnalyzer.comprehensiveURLAnalysis(urls[0])
          
          // Combine URL intelligence with text analysis
          const combinedScore = Math.round((result.aiScore * 0.7) + (urlAnalysis.riskScore * 0.3))
          
          return {
            ...result,
            aiScore: combinedScore,
            flags: [...new Set([...result.flags, ...urlAnalysis.threatCategories])],
            urlIntelligence: {
              domain: urlAnalysis.domain,
              reputation: urlAnalysis.reputation,
              riskScore: urlAnalysis.riskScore,
              threatCategories: urlAnalysis.threatCategories
            }
          } as EnhancedAIResult
        } catch (urlError) {
          console.warn('URL analysis failed:', urlError)
        }
      }
      
      return result as EnhancedAIResult
    }
  } catch (error) {
    console.warn('Advanced AI analysis failed, falling back to heuristics:', error)
  }
  
  // Fallback to simple heuristics
  const flags: string[] = []
  let aiScore = 15 // Base score
  
  // Enhanced heuristic patterns
  const patterns = {
    phishing: /free\s+crypto|airdrop|seed\sphrase|private\skey|2fa\s+reset|urgent\s+verify|account\s+suspended/i,
    malware: /download\s+exe|apk|crack|keygen|\.exe|\.scr|\.bat/i,
    scam: /investment\s+opportunity|guaranteed\s+profit|double\s+your\s+money|limited\s+time/i,
    social: /congratulations|winner|prize|lottery|inheritance|tax\s+refund/i,
    urgency: /urgent|immediate|expires?|deadline|act\s+now|limited\s+spots/i,
    financial: /send\s+money|wire\s+transfer|bitcoin|crypto|paypal|venmo|cashapp/i
  }
  
  Object.entries(patterns).forEach(([category, pattern]) => {
    if (pattern.test(text)) {
      flags.push(category)
      switch (category) {
        case 'phishing': aiScore += 25; break
        case 'malware': aiScore += 30; break
        case 'scam': aiScore += 20; break
        case 'social': aiScore += 15; break
        case 'urgency': aiScore += 10; break
        case 'financial': aiScore += 18; break
      }
    }
  })
  
  // URL analysis for basic mode
  const urlRegex = /https?:\/\/[^\s]+/g
  const urls = text.match(urlRegex)
  if (urls) {
    urls.forEach(url => {
      const domain = url.replace(/https?:\/\/(www\.)?/, '').split('/')[0]
      if (['bit.ly', 'tinyurl.com', 'grabify.link'].some(suspicious => domain.includes(suspicious))) {
        flags.push('suspicious_url')
        aiScore += 20
      }
    })
  }
  
  return {
    aiScore: Math.min(aiScore, 95),
    flags,
    provider: 'enhanced_heuristics'
  }
}
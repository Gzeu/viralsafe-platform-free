export interface RiskAssessment {
  score: number
  level: 'low' | 'medium' | 'high'
  reasons: string[]
  confidence: number
}

export interface AIResult {
  aiScore: number
  flags: string[]
  provider: string
  processingTimeMs?: number
  confidence?: number
}

export function computeRiskScore(input: {
  aiScore?: number
  aiConfidence?: number
  flags: string[]
  url?: string
  platform?: string
  vtVerdict?: string
}): RiskAssessment {
  let score = 0
  let confidence = 50
  const reasons: string[] = []

  // AI Analysis Score (0-60 points)
  if (input.aiScore !== undefined) {
    const aiWeight = (input.aiConfidence || 50) / 100
    const aiContribution = (input.aiScore / 100) * 60 * aiWeight
    score += aiContribution
    confidence = Math.max(confidence, input.aiConfidence || 50)
    
    if (input.aiScore > 70) reasons.push('High AI risk assessment')
    else if (input.aiScore > 40) reasons.push('Moderate AI risk assessment')
    else reasons.push('Low AI risk assessment')
  }

  // Flag-based scoring (0-30 points)
  const flagScores: Record<string, number> = {
    'phishing': 25,
    'scam': 25,
    'malware': 30,
    'misinformation': 15,
    'suspicious_link': 20,
    'investment_scam': 25,
    'crypto_scam': 20,
    'social_engineering': 20
  }

  for (const flag of input.flags) {
    const flagScore = flagScores[flag] || 5
    score += flagScore
    reasons.push(`Detected: ${flag.replace(/_/g, ' ')}`)
  }

  // URL-based analysis (0-15 points)
  if (input.url) {
    const url = input.url.toLowerCase()
    
    // Suspicious domains
    if (/\.(tk|ml|ga|cf)$/i.test(url)) {
      score += 10
      reasons.push('Suspicious top-level domain')
    }
    
    // URL shorteners
    if (/bit\.ly|tinyurl|t\.co|short\.link|grabify|iplogger/i.test(url)) {
      score += 15
      reasons.push('URL shortener detected')
    }
    
    // Suspicious patterns
    if (/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/.test(url)) {
      score += 5
      reasons.push('IP address instead of domain')
    }
    
    if (url.includes('login') && !url.includes('accounts.google.com') && !url.includes('login.microsoftonline.com')) {
      score += 8
      reasons.push('Suspicious login page')
    }
  }

  // Platform-specific adjustments (0-5 points)
  if (input.platform) {
    const highRiskPlatforms = ['telegram', 'whatsapp', 'sms']
    if (highRiskPlatforms.includes(input.platform.toLowerCase())) {
      score += 3
      reasons.push(`High-abuse platform: ${input.platform}`)
    }
  }

  // VirusTotal verdict (0-20 points)
  if (input.vtVerdict) {
    if (input.vtVerdict === 'malicious') {
      score += 20
      reasons.push('VirusTotal: Malicious URL detected')
      confidence = Math.max(confidence, 90)
    } else if (input.vtVerdict === 'suspicious') {
      score += 10
      reasons.push('VirusTotal: Suspicious activity')
      confidence = Math.max(confidence, 80)
    } else if (input.vtVerdict === 'harmless') {
      confidence = Math.max(confidence, 70)
      reasons.push('VirusTotal: URL appears safe')
    }
  }

  // Normalize score (0-100)
  score = Math.max(0, Math.min(100, score))
  
  // Determine risk level
  let level: 'low' | 'medium' | 'high'
  if (score >= 70) {
    level = 'high'
  } else if (score >= 40) {
    level = 'medium'
  } else {
    level = 'low'
  }

  // Adjust confidence based on available data sources
  const dataSources = [
    input.aiScore !== undefined,
    input.flags.length > 0,
    input.vtVerdict !== undefined
  ].filter(Boolean).length
  
  confidence = Math.min(confidence + (dataSources * 10), 100)

  return {
    score: Math.round(score * 10) / 10, // Round to 1 decimal
    level,
    reasons,
    confidence: Math.round(confidence)
  }
}

export async function classifyText(text: string): Promise<AIResult> {
  // Fallback to simple heuristics (no AI API keys required)
  const flags: string[] = []
  let score = 15 // Base score
  
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
        case 'phishing': score += 25; break
        case 'malware': score += 30; break
        case 'scam': score += 20; break
        case 'social': score += 15; break
        case 'urgency': score += 10; break
        case 'financial': score += 18; break
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
        score += 20
      }
    })
  }
  
  return {
    aiScore: Math.min(score, 95),
    flags,
    provider: 'enhanced_heuristics',
    confidence: flags.length > 0 ? 75 : 30,
    processingTimeMs: 50
  }
}
export interface RiskAssessment {
  score: number
  level: 'low' | 'medium' | 'high'
  reasons: string[]
  confidence: number
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
  const providers = [
    { name: 'groq', fn: callGroq, enabled: !!GROQ_API_KEY },
    { name: 'openai', fn: callOpenAI, enabled: !!OPENAI_API_KEY },
  ].filter(p => p.enabled)

  let lastError: any
  
  // Try AI providers in order
  for (const provider of providers) {
    try {
      const result = await provider.fn(text)
      return { ...result, provider: provider.name }
    } catch (error) {
      console.warn(`AI provider ${provider.name} failed:`, error)
      lastError = error
    }
  }

  // Fallback to heuristic analysis
  console.log('All AI providers failed, using heuristics:', lastError)
  return heuristicAnalysis(text)
}

function heuristicAnalysis(text: string): AIResult {
  const start = Date.now()
  const flags: string[] = []
  let score = 0

  // Phishing patterns
  if (/urgent.{0,20}action|act.{0,10}now|limited.{0,10}time|expire.{0,10}soon/i.test(text)) {
    flags.push('phishing')
    score += 30
  }

  // Crypto/financial scams
  if (/free.{0,10}crypto|airdrop|seed.{0,10}phrase|private.{0,10}key|wallet.{0,10}connect/i.test(text)) {
    flags.push('crypto_scam')
    score += 40
  }

  // Investment scams
  if (/guaranteed.{0,20}profit|double.{0,10}money|risk.{0,10}free|get.{0,10}rich.{0,10}quick/i.test(text)) {
    flags.push('investment_scam')
    score += 35
  }

  // Social engineering
  if (/verify.{0,10}account|suspended.{0,10}account|click.{0,10}here|download.{0,10}now/i.test(text)) {
    flags.push('social_engineering')
    score += 25
  }

  // Suspicious URLs in content
  if (/https?:\/\/[^\s]+/g.test(text)) {
    const urls = text.match(/https?:\/\/[^\s]+/g) || []
    for (const url of urls) {
      if (/bit\.ly|tinyurl|grabify|iplogger/i.test(url)) {
        flags.push('suspicious_link')
        score += 15
      }
    }
  }

  return {
    aiScore: Math.min(score, 100),
    confidence: flags.length > 0 ? 75 : 30,
    flags,
    provider: 'heuristics',
    processingTimeMs: Date.now() - start
  }
}
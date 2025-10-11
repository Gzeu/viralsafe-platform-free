import crypto from 'crypto'

export interface AIResult {
  aiScore: number
  confidence: number
  flags: string[]
  provider: string
  processingTimeMs: number
}

const GROQ_API_KEY = process.env.GROQ_API_KEY
const OPENAI_API_KEY = process.env.OPENAI_API_KEY
const GEMINI_API_KEY = process.env.GEMINI_API_KEY

async function callGroq(text: string): Promise<Omit<AIResult, 'provider'>> {
  const start = Date.now()
  const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${GROQ_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'llama3-70b-8192',
      messages: [{
        role: 'system',
        content: `You are a content safety analyzer. Analyze the content for potential risks like scams, phishing, malware, misinformation, or harmful content. Respond with a JSON object containing:
{
  "riskScore": number (0-100),
  "confidence": number (0-100),
  "flags": string[] (e.g. ["phishing", "scam", "malware", "misinformation"]),
  "reasoning": string
}`
      }, {
        role: 'user',
        content: `Analyze this content: "${text.slice(0, 1000)}"`
      }]
    })
  })

  if (!response.ok) {
    throw new Error(`Groq API failed: ${response.status}`)
  }

  const data = await response.json()
  const content = data.choices[0]?.message?.content
  
  try {
    const result = JSON.parse(content)
    return {
      aiScore: result.riskScore || 0,
      confidence: result.confidence || 50,
      flags: Array.isArray(result.flags) ? result.flags : [],
      processingTimeMs: Date.now() - start
    }
  } catch {
    // Fallback parsing
    const score = content.includes('high risk') ? 80 : content.includes('medium risk') ? 50 : 20
    return {
      aiScore: score,
      confidence: 60,
      flags: [],
      processingTimeMs: Date.now() - start
    }
  }
}

async function callOpenAI(text: string): Promise<Omit<AIResult, 'provider'>> {
  const start = Date.now()
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${OPENAI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [{
        role: 'system',
        content: 'Analyze content safety and return JSON: {"riskScore": 0-100, "confidence": 0-100, "flags": ["phishing"|"scam"|"malware"|"misinformation"]}'
      }, {
        role: 'user',
        content: `Analyze: "${text.slice(0, 1000)}"`
      }]
    })
  })

  if (!response.ok) {
    throw new Error(`OpenAI API failed: ${response.status}`)
  }

  const data = await response.json()
  const content = data.choices[0]?.message?.content
  
  try {
    const result = JSON.parse(content)
    return {
      aiScore: result.riskScore || 0,
      confidence: result.confidence || 50,
      flags: Array.isArray(result.flags) ? result.flags : [],
      processingTimeMs: Date.now() - start
    }
  } catch {
    const score = content.includes('high') ? 70 : content.includes('medium') ? 40 : 15
    return {
      aiScore: score,
      confidence: 50,
      flags: [],
      processingTimeMs: Date.now() - start
    }
  }
}

function heuristicAnalysis(text: string): Omit<AIResult, 'provider'> {
  const start = Date.now()
  const flags: string[] = []
  let score = 0

  // Phishing indicators
  if (/urgent.{0,20}action|act.{0,10}now|limited.{0,10}time/i.test(text)) {
    flags.push('phishing')
    score += 25
  }

  // Crypto scams
  if (/free.{0,10}crypto|airdrop|seed.{0,10}phrase|private.{0,10}key|wallet.{0,10}connect/i.test(text)) {
    flags.push('scam')
    score += 35
  }

  // Suspicious links
  if (/bit\.ly|tinyurl|t\.co|short\.link|grabify|iplogger/i.test(text)) {
    flags.push('suspicious_link')
    score += 20
  }

  // Investment scams
  if (/guaranteed.{0,20}profit|double.{0,10}money|risk.{0,10}free|get.{0,10}rich/i.test(text)) {
    flags.push('investment_scam')
    score += 30
  }

  return {
    aiScore: Math.min(score, 100),
    confidence: flags.length > 0 ? 70 : 40,
    flags,
    processingTimeMs: Date.now() - start
  }
}

export async function classifyText(text: string): Promise<AIResult> {
  const providers = [
    { name: 'groq', fn: callGroq, enabled: !!GROQ_API_KEY },
    { name: 'openai', fn: callOpenAI, enabled: !!OPENAI_API_KEY },
  ].filter(p => p.enabled)

  // Try AI providers first
  for (const provider of providers) {
    try {
      const result = await provider.fn(text)
      return { ...result, provider: provider.name }
    } catch (error) {
      console.warn(`AI provider ${provider.name} failed:`, error)
    }
  }

  // Fallback to heuristics
  const result = heuristicAnalysis(text)
  return { ...result, provider: 'heuristics' }
}
import { OpenAI } from 'openai'
import { GoogleGenerativeAI } from '@google/generative-ai'
import Groq from 'groq-sdk'

interface AIResult {
  aiScore: number
  flags: string[]
  provider: string
  confidence: number
  threatLevel: 'low' | 'medium' | 'high' | 'critical'
  analysis: {
    sentiment: number
    urgency: number
    deception: number
    financialRisk: number
  }
  detectedPatterns: string[]
}

interface ThreatIntelligence {
  knownMaliciousDomains: string[]
  phishingPatterns: RegExp[]
  scamKeywords: string[]
  socialEngineeringTactics: string[]
}

// Advanced Threat Intelligence Database
const THREAT_INTEL: ThreatIntelligence = {
  knownMaliciousDomains: [
    'bit.ly', 'tinyurl.com', 'grabify.link', 'iplogger.org', 
    'discord.gg', 'telegram.me', '2no.co', 'cutt.ly',
    'short.gy', 'rebrand.ly', 'ow.ly', 't.co'
  ],
  
  phishingPatterns: [
    /urgent.{0,20}(verify|update|confirm)/i,
    /account.{0,20}(suspended|locked|limited)/i,
    /(click|tap).{0,10}(here|link|now)/i,
    /limited.{0,10}time.{0,10}offer/i,
    /(free|earn).{0,20}(crypto|bitcoin|eth|money)/i,
    /seed.{0,10}phrase|private.{0,10}key/i,
    /(congratulations|winner).{0,30}(prize|reward)/i,
    /security.{0,20}(alert|warning|notice)/i
  ],
  
  scamKeywords: [
    'airdrop', 'giveaway', 'double your', 'investment opportunity',
    'guaranteed profit', 'risk-free', 'limited spots', 'exclusive access',
    'verify identity', 'confirm payment', 'update billing', 'suspended account',
    'tax refund', 'prize winner', 'lottery', 'inheritance',
    'romantic interest', 'military deployment', 'stranded abroad'
  ],
  
  socialEngineeringTactics: [
    'urgency', 'fear', 'greed', 'authority', 'social proof', 'scarcity',
    'reciprocity', 'curiosity', 'sympathy', 'trust exploitation'
  ]
}

// Advanced Pattern Detection
class SecurityAnalyzer {
  private static detectPhishingPatterns(text: string): { score: number; patterns: string[] } {
    let score = 0
    const detectedPatterns: string[] = []
    
    THREAT_INTEL.phishingPatterns.forEach((pattern, index) => {
      if (pattern.test(text)) {
        score += 15 + (index * 2) // Different weights for different patterns
        detectedPatterns.push(`phishing_pattern_${index}`)
      }
    })
    
    return { score: Math.min(score, 80), patterns: detectedPatterns }
  }
  
  private static detectScamKeywords(text: string): { score: number; keywords: string[] } {
    let score = 0
    const detectedKeywords: string[] = []
    
    THREAT_INTEL.scamKeywords.forEach(keyword => {
      if (new RegExp(keyword, 'i').test(text)) {
        score += 8
        detectedKeywords.push(keyword)
      }
    })
    
    return { score: Math.min(score, 60), keywords: detectedKeywords }
  }
  
  private static analyzeSentiment(text: string): number {
    const urgentWords = /urgent|immediate|now|quickly|hurry|expire|deadline/gi
    const fearWords = /danger|risk|loss|suspended|banned|illegal|arrest/gi
    const greedWords = /free|profit|earn|win|bonus|reward|money|cash/gi
    
    let sentiment = 0
    sentiment += (text.match(urgentWords) || []).length * 5
    sentiment += (text.match(fearWords) || []).length * 7
    sentiment += (text.match(greedWords) || []).length * 6
    
    return Math.min(sentiment, 50)
  }
  
  private static detectSocialEngineering(text: string): { score: number; tactics: string[] } {
    const tactics: string[] = []
    let score = 0
    
    // Authority exploitation
    if (/official|government|bank|police|security|admin/i.test(text)) {
      tactics.push('authority')
      score += 12
    }
    
    // Urgency creation
    if (/urgent|immediate|expires?|deadline|limited time/i.test(text)) {
      tactics.push('urgency')
      score += 10
    }
    
    // Fear induction
    if (/suspended|locked|banned|illegal|arrest|fine/i.test(text)) {
      tactics.push('fear')
      score += 15
    }
    
    // Scarcity
    if (/limited|exclusive|only \d+|last chance/i.test(text)) {
      tactics.push('scarcity')
      score += 8
    }
    
    return { score: Math.min(score, 45), tactics }
  }
  
  public static comprehensiveAnalysis(text: string): Omit<AIResult, 'provider'> {
    const phishing = this.detectPhishingPatterns(text)
    const scam = this.detectScamKeywords(text)
    const sentiment = this.analyzeSentiment(text)
    const socialEng = this.detectSocialEngineering(text)
    
    const totalScore = phishing.score + scam.score + sentiment + socialEng.score
    const confidence = Math.min(85 + (totalScore * 0.15), 95)
    
    let threatLevel: AIResult['threatLevel'] = 'low'
    if (totalScore >= 70) threatLevel = 'critical'
    else if (totalScore >= 50) threatLevel = 'high'
    else if (totalScore >= 25) threatLevel = 'medium'
    
    const flags: string[] = []
    if (phishing.patterns.length > 0) flags.push('phishing')
    if (scam.keywords.length > 0) flags.push('scam')
    if (socialEng.tactics.includes('authority')) flags.push('impersonation')
    if (socialEng.tactics.includes('fear')) flags.push('intimidation')
    if (text.length < 50 && totalScore > 30) flags.push('suspicious_brevity')
    
    return {
      aiScore: Math.min(totalScore, 95),
      flags,
      confidence,
      threatLevel,
      analysis: {
        sentiment: sentiment / 50,
        urgency: socialEng.tactics.includes('urgency') ? 0.8 : 0.2,
        deception: phishing.score / 80,
        financialRisk: scam.score / 60
      },
      detectedPatterns: [...phishing.patterns, ...scam.keywords, ...socialEng.tactics]
    }
  }
}

// AI Provider Implementations
class OpenAIAnalyzer {
  private static openai = process.env.OPENAI_API_KEY ? new OpenAI({ apiKey: process.env.OPENAI_API_KEY }) : null
  
  static async analyze(text: string): Promise<AIResult | null> {
    if (!this.openai) return null
    
    try {
      const completion = await this.openai.chat.completions.create({
        model: "gpt-3.5-turbo",
        messages: [{
          role: "system",
          content: "You are a cybersecurity expert analyzing text for phishing, scams, and malicious content. Respond with JSON only: {\"score\": 0-100, \"threat_level\": \"low/medium/high/critical\", \"flags\": [\"flag1\", \"flag2\"], \"confidence\": 0-100}"
        }, {
          role: "user",
          content: `Analyze this text for security threats: "${text}"`
        }],
        temperature: 0.3,
        max_tokens: 200
      })
      
      const result = JSON.parse(completion.choices[0].message.content || '{}')
      return {
        aiScore: result.score || 0,
        flags: result.flags || [],
        provider: 'openai',
        confidence: result.confidence || 50,
        threatLevel: result.threat_level || 'low',
        analysis: {
          sentiment: result.score / 100,
          urgency: result.flags?.includes('urgency') ? 0.8 : 0.2,
          deception: result.flags?.includes('phishing') ? 0.9 : 0.1,
          financialRisk: result.flags?.includes('financial') ? 0.8 : 0.2
        },
        detectedPatterns: result.flags || []
      }
    } catch (error) {
      console.error('OpenAI analysis failed:', error)
      return null
    }
  }
}

class GroqAnalyzer {
  private static groq = process.env.GROQ_API_KEY ? new Groq({ apiKey: process.env.GROQ_API_KEY }) : null
  
  static async analyze(text: string): Promise<AIResult | null> {
    if (!this.groq) return null
    
    try {
      const completion = await this.groq.chat.completions.create({
        messages: [{
          role: "system",
          content: "Cybersecurity analysis: Rate text 0-100 for threats. JSON format: {\"score\": number, \"threat_level\": string, \"flags\": array, \"confidence\": number}"
        }, {
          role: "user", 
          content: `Security scan: "${text}"`
        }],
        model: "mixtral-8x7b-32768",
        temperature: 0.2,
        max_tokens: 150
      })
      
      const result = JSON.parse(completion.choices[0].message.content || '{}')
      return {
        aiScore: result.score || 0,
        flags: result.flags || [],
        provider: 'groq',
        confidence: result.confidence || 50,
        threatLevel: result.threat_level || 'low',
        analysis: {
          sentiment: result.score / 100,
          urgency: 0.5,
          deception: result.score > 50 ? 0.7 : 0.2,
          financialRisk: result.flags?.includes('financial') ? 0.8 : 0.3
        },
        detectedPatterns: result.flags || []
      }
    } catch (error) {
      console.error('Groq analysis failed:', error)
      return null
    }
  }
}

class GeminiAnalyzer {
  private static gemini = process.env.GEMINI_API_KEY ? new GoogleGenerativeAI(process.env.GEMINI_API_KEY) : null
  
  static async analyze(text: string): Promise<AIResult | null> {
    if (!this.gemini) return null
    
    try {
      const model = this.gemini.getGenerativeModel({ model: "gemini-pro" })
      const prompt = `Security Analysis - Rate this text 0-100 for cyber threats. JSON only: {"score": number, "threat_level": "low/medium/high/critical", "flags": ["threats"], "confidence": number}\n\nText: "${text}"`
      
      const result = await model.generateContent(prompt)
      const response = await result.response
      const jsonResult = JSON.parse(response.text().replace(/```json|```/g, ''))
      
      return {
        aiScore: jsonResult.score || 0,
        flags: jsonResult.flags || [],
        provider: 'gemini',
        confidence: jsonResult.confidence || 50,
        threatLevel: jsonResult.threat_level || 'low',
        analysis: {
          sentiment: jsonResult.score / 100,
          urgency: 0.4,
          deception: jsonResult.score > 60 ? 0.8 : 0.2,
          financialRisk: jsonResult.flags?.includes('financial') ? 0.9 : 0.2
        },
        detectedPatterns: jsonResult.flags || []
      }
    } catch (error) {
      console.error('Gemini analysis failed:', error)
      return null
    }
  }
}

// Main Advanced AI Classification
export async function advancedClassifyText(text: string): Promise<AIResult> {
  // Multi-layer analysis approach
  const analyses: (AIResult | null)[] = await Promise.allSettled([
    OpenAIAnalyzer.analyze(text),
    GroqAnalyzer.analyze(text), 
    GeminiAnalyzer.analyze(text)
  ]).then(results => results.map(r => r.status === 'fulfilled' ? r.value : null))
  
  // Get heuristic analysis as baseline
  const heuristicResult = SecurityAnalyzer.comprehensiveAnalysis(text)
  
  // Filter successful AI analyses
  const validAnalyses = analyses.filter((a): a is AIResult => a !== null)
  
  if (validAnalyses.length === 0) {
    // Fallback to enhanced heuristics
    return {
      ...heuristicResult,
      provider: 'advanced_heuristics'
    }
  }
  
  // Ensemble AI + Heuristics (weighted combination)
  const aiAverage = validAnalyses.reduce((sum, analysis) => ({
    aiScore: sum.aiScore + (analysis.aiScore * analysis.confidence / 100),
    confidence: sum.confidence + analysis.confidence,
    flags: [...new Set([...sum.flags, ...analysis.flags])]
  }), { aiScore: 0, confidence: 0, flags: [] as string[] })
  
  // Weight: 60% AI ensemble + 40% heuristics
  const finalScore = Math.round(
    (aiAverage.aiScore / validAnalyses.length) * 0.6 + 
    heuristicResult.aiScore * 0.4
  )
  
  const avgConfidence = aiAverage.confidence / validAnalyses.length
  const combinedFlags = [...new Set([...aiAverage.flags, ...heuristicResult.flags])]
  
  let finalThreatLevel: AIResult['threatLevel'] = 'low'
  if (finalScore >= 80) finalThreatLevel = 'critical'
  else if (finalScore >= 60) finalThreatLevel = 'high'
  else if (finalScore >= 35) finalThreatLevel = 'medium'
  
  return {
    aiScore: finalScore,
    flags: combinedFlags,
    provider: `ensemble_${validAnalyses.map(a => a.provider).join('+')}_heuristics`,
    confidence: Math.round(avgConfidence * 0.7 + heuristicResult.confidence * 0.3),
    threatLevel: finalThreatLevel,
    analysis: {
      sentiment: (validAnalyses.reduce((sum, a) => sum + a.analysis.sentiment, 0) / validAnalyses.length + heuristicResult.analysis.sentiment) / 2,
      urgency: Math.max(...validAnalyses.map(a => a.analysis.urgency), heuristicResult.analysis.urgency),
      deception: Math.max(...validAnalyses.map(a => a.analysis.deception), heuristicResult.analysis.deception),
      financialRisk: Math.max(...validAnalyses.map(a => a.analysis.financialRisk), heuristicResult.analysis.financialRisk)
    },
    detectedPatterns: [...new Set([...validAnalyses.flatMap(a => a.detectedPatterns), ...heuristicResult.detectedPatterns])]
  }
}
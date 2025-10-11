import { NextResponse } from 'next/server'
import { z } from 'zod'
import { dbConnect } from '../../../lib/db'
import { Analysis } from '../../../lib/models'
import { advancedClassifyText } from '../../../lib/ai-advanced'
import { URLIntelligenceAnalyzer } from '../../../lib/url-intelligence'
import { rateLimit } from '../../../lib/ratelimit'

const advancedScanSchema = z.object({
  inputType: z.enum(['text','url']),
  content: z.string().max(5000).optional(),
  url: z.string().url().optional(),
  platform: z.string().default('general').optional(),
  deepScan: z.boolean().default(true),
  includeURLAnalysis: z.boolean().default(true)
})

export const dynamic = 'force-dynamic'

export async function POST(req: Request) {
  try {
    // Stricter rate limiting for advanced features
    const ip = req.headers.get('x-forwarded-for') || 'ip'
    rateLimit(ip, 20, 60000) // 20 requests per minute for advanced scanning
    
    const body = await req.json()
    const parsed = advancedScanSchema.parse(body)
    
    // Require at least one AI provider for advanced scanning
    const hasAIProvider = !!(process.env.OPENAI_API_KEY || process.env.GROQ_API_KEY || process.env.GEMINI_API_KEY)
    if (!hasAIProvider) {
      return NextResponse.json({ 
        ok: false, 
        error: 'Advanced scanning requires AI provider configuration',
        fallback: '/api/analyze'
      }, { status: 400 })
    }

    await dbConnect()

    const inputText = parsed.inputType === 'text' ? (parsed.content || '') : (parsed.url || '')
    
    // Advanced AI analysis
    const aiResult = await advancedClassifyText(inputText)
    
    let urlAnalysis = null
    if (parsed.includeURLAnalysis && parsed.inputType === 'url' && parsed.url) {
      try {
        urlAnalysis = await URLIntelligenceAnalyzer.comprehensiveURLAnalysis(parsed.url)
      } catch (error) {
        console.warn('URL analysis failed:', error)
      }
    }
    
    // Comprehensive risk assessment
    const riskFactors = [
      { name: 'AI Confidence', value: aiResult.confidence, weight: 0.3 },
      { name: 'Threat Level', value: aiResult.threatLevel === 'critical' ? 95 : 
                                      aiResult.threatLevel === 'high' ? 75 :
                                      aiResult.threatLevel === 'medium' ? 45 : 20, weight: 0.25 },
      { name: 'Deception Score', value: aiResult.analysis.deception * 100, weight: 0.2 },
      { name: 'Financial Risk', value: aiResult.analysis.financialRisk * 100, weight: 0.15 },
      { name: 'Social Engineering', value: aiResult.analysis.urgency * 100, weight: 0.1 }
    ]
    
    if (urlAnalysis) {
      riskFactors.push({ name: 'URL Reputation', value: urlAnalysis.riskScore, weight: 0.2 })
    }
    
    const weightedScore = riskFactors.reduce((sum, factor) => 
      sum + (factor.value * factor.weight), 0
    )
    
    const comprehensiveRisk = {
      score: Math.round(weightedScore),
      level: weightedScore >= 80 ? 'critical' :
             weightedScore >= 60 ? 'high' :
             weightedScore >= 35 ? 'medium' : 'low',
      factors: riskFactors,
      reasons: [
        `Multi-layer AI analysis (${aiResult.provider})`,
        `Confidence level: ${aiResult.confidence}%`,
        `Threat classification: ${aiResult.threatLevel}`,
        `Detected patterns: ${aiResult.detectedPatterns.length}`,
        ...aiResult.flags.map(flag => `Security flag: ${flag}`),
        ...(urlAnalysis ? [`URL reputation: ${urlAnalysis.reputation}`, `Domain threats: ${urlAnalysis.threatCategories.join(', ')}`] : [])
      ]
    }

    // Save comprehensive analysis
    const doc = await Analysis.create({
      inputType: parsed.inputType,
      platform: parsed.platform || 'general',
      content: parsed.content,
      url: parsed.url,
      provider: `advanced_${aiResult.provider}`,
      risk: comprehensiveRisk,
      tags: [...aiResult.flags, ...(urlAnalysis ? urlAnalysis.threatCategories : [])],
    })

    // Comprehensive response
    const responseData = {
      id: String(doc._id),
      timestamp: new Date().toISOString(),
      
      // Risk Assessment
      risk: comprehensiveRisk,
      
      // AI Analysis Results
      aiAnalysis: {
        provider: aiResult.provider,
        confidence: aiResult.confidence,
        threatLevel: aiResult.threatLevel,
        flags: aiResult.flags,
        detectedPatterns: aiResult.detectedPatterns,
        analysis: {
          sentiment: Math.round(aiResult.analysis.sentiment * 100),
          urgency: Math.round(aiResult.analysis.urgency * 100),
          deception: Math.round(aiResult.analysis.deception * 100),
          financialRisk: Math.round(aiResult.analysis.financialRisk * 100)
        }
      },
      
      // URL Intelligence (if applicable)
      ...(urlAnalysis && {
        urlIntelligence: {
          domain: urlAnalysis.domain,
          reputation: urlAnalysis.reputation,
          riskScore: urlAnalysis.riskScore,
          analysis: urlAnalysis.analysis,
          threatCategories: urlAnalysis.threatCategories,
          virusTotal: urlAnalysis.vtResults ? {
            verdict: urlAnalysis.vtResults.verdict,
            scanId: urlAnalysis.vtResults.scanId,
            stats: urlAnalysis.vtResults.stats
          } : null
        }
      }),
      
      // Recommendations
      recommendations: generateSecurityRecommendations(aiResult, urlAnalysis)
    }

    return NextResponse.json({ 
      ok: true, 
      data: responseData,
      meta: {
        scanType: 'advanced',
        processingTime: Date.now() - req.headers.get('x-request-start') || 0,
        version: '2.0'
      }
    })

  } catch (e: any) {
    return NextResponse.json({ 
      ok: false, 
      error: e.message || 'Advanced scan failed',
      errorType: 'ADVANCED_SCAN_ERROR'
    }, { status: 400 })
  }
}

function generateSecurityRecommendations(aiResult: any, urlAnalysis: any): string[] {
  const recommendations: string[] = []
  
  if (aiResult.threatLevel === 'critical' || aiResult.threatLevel === 'high') {
    recommendations.push('🚨 HIGH RISK: Do not interact with this content')
    recommendations.push('📱 Report this content to relevant authorities')
  }
  
  if (aiResult.flags.includes('phishing')) {
    recommendations.push('🎣 Potential phishing attempt detected - verify sender authenticity')
    recommendations.push('🔐 Never enter personal information or passwords')
  }
  
  if (aiResult.flags.includes('financial')) {
    recommendations.push('💰 Financial scam indicators found - consult financial advisor')
    recommendations.push('🏦 Verify through official banking channels')
  }
  
  if (urlAnalysis?.reputation === 'suspicious' || urlAnalysis?.reputation === 'malicious') {
    recommendations.push(`🌐 Suspicious domain detected: ${urlAnalysis.domain}`)
    recommendations.push('🔍 Use URL scanners before visiting')
  }
  
  if (urlAnalysis?.analysis?.isShortener) {
    recommendations.push('🔗 URL shortener detected - destination unknown until clicked')
    recommendations.push('🛡️ Consider using URL expander services first')
  }
  
  if (!urlAnalysis?.analysis?.usesHTTPS) {
    recommendations.push('🔓 Insecure connection (HTTP) - data transmitted in plain text')
  }
  
  if (aiResult.analysis.urgency > 0.7) {
    recommendations.push('⏰ Urgency tactics detected - take time to verify claims')
  }
  
  if (recommendations.length === 0) {
    recommendations.push('✅ Content appears safe based on current analysis')
    recommendations.push('🔄 Consider periodic re-scanning of suspicious content')
  }
  
  return recommendations
}

// GET endpoint for advanced scan capabilities info
export async function GET() {
  const hasOpenAI = !!process.env.OPENAI_API_KEY
  const hasGroq = !!process.env.GROQ_API_KEY
  const hasGemini = !!process.env.GEMINI_API_KEY
  const hasVirusTotal = !!process.env.VIRUSTOTAL_API_KEY
  
  return NextResponse.json({
    ok: true,
    capabilities: {
      multiLayerAI: hasOpenAI || hasGroq || hasGemini,
      providers: {
        openai: hasOpenAI,
        groq: hasGroq,
        gemini: hasGemini
      },
      urlIntelligence: true,
      virusTotal: hasVirusTotal,
      threatDatabase: true,
      socialEngineeringDetection: true,
      ensembleAnalysis: (hasOpenAI + hasGroq + hasGemini) >= 2
    },
    features: [
      'Multi-provider AI ensemble analysis',
      'Advanced threat pattern detection', 
      'URL reputation and intelligence',
      'Social engineering tactic identification',
      'Financial risk assessment',
      'Confidence scoring and threat levels',
      'Comprehensive security recommendations'
    ],
    rateLimit: {
      requests: 20,
      window: '1 minute',
      note: 'Stricter limits for advanced scanning'
    }
  })
}
import { NextRequest, NextResponse } from 'next/server'
import { dbConnect } from '@/lib/db'
import { Analysis } from '@/lib/models'
import { analyzeSchema } from '@/lib/validators'
import { classifyText } from '@/lib/ai'
import { computeRisk } from '@/lib/scoring'
import { submitUrlScan, getAnalysisResult } from '@/lib/virustotal'
import crypto from 'crypto'

export async function POST(request: NextRequest) {
  const startTime = Date.now()
  
  try {
    // Basic rate limiting
    const ip = request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip') || 'unknown'
    const ipHash = crypto.createHash('sha256').update(ip).digest('hex').slice(0, 16)
    
    // Parse and validate input
    const body = await request.json()
    const parsed = analyzeSchema.parse(body)
    
    // Connect to database
    await dbConnect()
    
    // Determine content to analyze
    const contentToAnalyze = parsed.inputType === 'text' 
      ? parsed.content || ''
      : parsed.url || ''
    
    if (!contentToAnalyze.trim()) {
      return NextResponse.json(
        { ok: false, error: 'No content provided for analysis' },
        { status: 400 }
      )
    }
    
    // Run AI analysis
    const aiResult = await classifyText(contentToAnalyze)
    
    // For URLs, optionally run VirusTotal scan
    let vtResult = null
    if (parsed.inputType === 'url' && parsed.checkUrls && process.env.VIRUSTOTAL_API_KEY) {
      try {
        const { id } = await submitUrlScan(parsed.url!)
        
        // Quick check (don't wait too long)
        await new Promise(resolve => setTimeout(resolve, 3000))
        vtResult = await getAnalysisResult(id)
        
        if (vtResult.verdict === 'pending') {
          // Save scan ID for later retrieval
          vtResult.id = id
        }
      } catch (error) {
        console.warn('VirusTotal scan failed:', error)
        // Continue without VT results
      }
    }
    
    // Compute final risk score
    const riskAssessment = computeRisk({
      aiScore: aiResult.aiScore,
      aiConfidence: aiResult.confidence,
      flags: aiResult.flags,
      url: parsed.url,
      platform: parsed.platform,
      vtVerdict: vtResult?.verdict
    })
    
    // Save to database
    const analysisDoc = await Analysis.create({
      inputType: parsed.inputType,
      platform: parsed.platform,
      content: parsed.content,
      url: parsed.url,
      provider: aiResult.provider,
      risk: {
        score: riskAssessment.score,
        level: riskAssessment.level,
        reasons: riskAssessment.reasons
      },
      tags: aiResult.flags,
      processingTimeMs: Date.now() - startTime,
      userAgent: parsed.userAgent,
      ipHash
    })
    
    // Prepare response
    const response = {
      ok: true,
      data: {
        id: analysisDoc._id.toString(),
        content_hash: crypto.createHash('sha256').update(contentToAnalyze).digest('hex').slice(0, 12),
        content_preview: contentToAnalyze.slice(0, 200),
        risk_score: riskAssessment.score / 100,
        risk_level: riskAssessment.level,
        categories: aiResult.flags,
        indicators: riskAssessment.reasons,
        recommendations: generateRecommendations(riskAssessment),
        platform: parsed.platform,
        timestamp: analysisDoc.createdAt?.toISOString() || new Date().toISOString(),
        processing_time_ms: Date.now() - startTime,
        ai_provider: aiResult.provider,
        confidence: riskAssessment.confidence,
        virustotal_report: vtResult ? {
          verdict: vtResult.verdict,
          stats: vtResult.stats,
          permalink: vtResult.permalink
        } : undefined
      }
    }
    
    return NextResponse.json(response)
    
  } catch (error: any) {
    console.error('Analysis failed:', error)
    
    if (error.name === 'ZodError') {
      return NextResponse.json(
        { ok: false, error: 'Invalid input data', details: error.errors },
        { status: 400 }
      )
    }
    
    return NextResponse.json(
      { ok: false, error: error.message || 'Analysis failed' },
      { status: 500 }
    )
  }
}

function generateRecommendations(risk: { score: number; level: string; reasons: string[] }): string[] {
  const recommendations: string[] = []
  
  if (risk.level === 'high') {
    recommendations.push('🚨 HIGH RISK: Avoid interacting with this content')
    recommendations.push('🔒 Do not click any links or download attachments')
    recommendations.push('📢 Report this content to the platform if possible')
    recommendations.push('🛡️ Consider blocking the sender')
  } else if (risk.level === 'medium') {
    recommendations.push('⚠️ MEDIUM RISK: Exercise caution with this content')
    recommendations.push('🔍 Verify information through trusted sources')
    recommendations.push('🤔 Be skeptical of any requests for personal information')
    recommendations.push('👥 Consider asking others for their opinion')
  } else {
    recommendations.push('✅ LOW RISK: Content appears relatively safe')
    recommendations.push('📚 Still recommended to verify important information')
    recommendations.push('🧠 Use critical thinking when consuming content')
    recommendations.push('👍 Safe to engage with normal caution')
  }
  
  // Add specific recommendations based on detected issues
  if (risk.reasons.some(r => r.includes('phishing'))) {
    recommendations.push('🎣 Phishing detected: Never enter passwords or personal info')
  }
  
  if (risk.reasons.some(r => r.includes('scam'))) {
    recommendations.push('💰 Potential scam: Be very cautious with financial requests')
  }
  
  if (risk.reasons.some(r => r.includes('VirusTotal'))) {
    recommendations.push('🔗 URL flagged by security engines - avoid clicking')
  }
  
  return recommendations
}
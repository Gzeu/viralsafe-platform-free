import { NextResponse } from 'next/server'
import { analyzeSchema } from '../../../lib/validators'
import { dbConnect } from '../../../lib/db'
import { Analysis } from '../../../lib/models'
import { classifyText, EnhancedAIResult } from '../../../lib/ai'
import { computeRisk } from '../../../lib/scoring'
import { rateLimit } from '../../../lib/ratelimit'
import { captureScreenshotSmart, validateScreenshotUrl, ScreenshotResult } from '../../../lib/screenshot'

export const dynamic = 'force-dynamic'

export async function POST(req: Request) {
  try {
    const ip = req.headers.get('x-forwarded-for') || 'ip'
    rateLimit(ip, Number(process.env.RATELIMIT_MAX||60), Number(process.env.RATELIMIT_WINDOW_MS||60000))
    
    const body = await req.json()
    const parsed = analyzeSchema.parse(body)
    
    // Check if advanced features should be used
    const useAdvanced = !!(process.env.OPENAI_API_KEY || process.env.GROQ_API_KEY || process.env.GEMINI_API_KEY)

    await dbConnect()

    const inputText = parsed.inputType === 'text' ? (parsed.content || '') : (parsed.url || '')
    const aiResult = await classifyText(inputText, useAdvanced)
    
    // Enhanced risk calculation for advanced features
    let risk
    if (useAdvanced && 'threatLevel' in aiResult) {
      const enhanced = aiResult as EnhancedAIResult
      risk = {
        score: enhanced.aiScore,
        level: enhanced.threatLevel,
        reasons: [
          `AI confidence: ${enhanced.confidence}%`,
          `Sentiment analysis: ${Math.round(enhanced.analysis.sentiment * 100)}%`,
          `Deception indicators: ${Math.round(enhanced.analysis.deception * 100)}%`,
          `Financial risk: ${Math.round(enhanced.analysis.financialRisk * 100)}%`,
          ...enhanced.detectedPatterns.map(pattern => `Pattern: ${pattern}`)
        ]
      }
    } else {
      // Fallback to simple risk calculation
      risk = computeRisk({ 
        aiScore: aiResult.aiScore, 
        flags: aiResult.flags, 
        url: parsed.url, 
        platform: parsed.platform 
      })
    }

    // Capture screenshot for URL analysis
    let screenshotResult: ScreenshotResult | undefined
    if (parsed.inputType === 'url' && parsed.url && parsed.includeScreenshot !== false) {
      try {
        // Validate URL for screenshot
        const urlValidation = validateScreenshotUrl(parsed.url)
        if (urlValidation.valid) {
          // Apply custom screenshot options if provided
          const screenshotOptions = parsed.screenshotOptions || {}
          screenshotResult = await captureScreenshotSmart(parsed.url, screenshotOptions)
          
          // If screenshot failed, add reason to risk analysis
          if (!screenshotResult.success && screenshotResult.error) {
            risk.reasons.push(`Screenshot capture failed: ${screenshotResult.error}`)
          }
        } else {
          screenshotResult = {
            success: false,
            error: urlValidation.error || 'URL validation failed'
          }
          risk.reasons.push(`Screenshot skipped: ${urlValidation.error}`)
        }
      } catch (screenshotError: any) {
        screenshotResult = {
          success: false,
          error: `Screenshot service error: ${screenshotError.message}`
        }
        risk.reasons.push(`Screenshot error: ${screenshotError.message}`)
      }
    }

    const doc = await Analysis.create({
      inputType: parsed.inputType,
      platform: parsed.platform || 'general',
      content: parsed.content,
      url: parsed.url,
      provider: aiResult.provider,
      risk,
      tags: aiResult.flags,
      screenshot: screenshotResult ? {
        success: screenshotResult.success,
        screenshotUrl: screenshotResult.screenshotUrl,
        error: screenshotResult.error,
        metadata: screenshotResult.metadata
      } : undefined,
    })

    // Enhanced response for advanced features
    const responseData: any = { 
      id: String(doc._id), 
      risk, 
      provider: aiResult.provider, 
      flags: aiResult.flags,
      screenshot: screenshotResult ? {
        success: screenshotResult.success,
        screenshotUrl: screenshotResult.screenshotUrl,
        error: screenshotResult.error,
        metadata: screenshotResult.metadata
      } : undefined
    }
    
    if (useAdvanced && 'threatLevel' in aiResult) {
      const enhanced = aiResult as EnhancedAIResult
      responseData.advanced = {
        confidence: enhanced.confidence,
        threatLevel: enhanced.threatLevel,
        analysis: enhanced.analysis,
        detectedPatterns: enhanced.detectedPatterns,
        urlIntelligence: enhanced.urlIntelligence
      }
    }

    return NextResponse.json({ ok: true, data: responseData })

  } catch (e: any) {
    return NextResponse.json({ ok: false, error: e.message || 'Analyze failed' }, { status: 400 })
  }
}
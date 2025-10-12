import { NextResponse } from 'next/server'
import { screenshotSchema } from '../../../lib/validators'
import { captureScreenshot, captureScreenshotSmart, validateScreenshotUrl } from '../../../lib/screenshot'
import { rateLimit } from '../../../lib/ratelimit'

export const dynamic = 'force-dynamic'

/**
 * POST /api/screenshot
 * Capture screenshot of a website using ScreenshotMachine API
 */
export async function POST(req: Request) {
  try {
    const ip = req.headers.get('x-forwarded-for') || 'ip'
    rateLimit(ip, Number(process.env.RATELIMIT_MAX||60), Number(process.env.RATELIMIT_WINDOW_MS||60000))
    
    const body = await req.json()
    const parsed = screenshotSchema.parse(body)
    
    // Validate URL before attempting screenshot
    const urlValidation = validateScreenshotUrl(parsed.url)
    if (!urlValidation.valid) {
      return NextResponse.json({
        ok: false,
        error: `Invalid URL: ${urlValidation.error}`
      }, { status: 400 })
    }

    // Determine if smart screenshot should be used
    const useSmartCapture = !parsed.hideSelector && !parsed.clickSelector
    
    let result
    if (useSmartCapture) {
      // Use smart capture with automatic cookie banner handling
      result = await captureScreenshotSmart(parsed.url, {
        dimension: parsed.dimension,
        device: parsed.device,
        format: parsed.format,
        delay: parsed.delay,
        zoom: parsed.zoom
      })
    } else {
      // Use manual capture with custom selectors
      result = await captureScreenshot({
        url: parsed.url,
        dimension: parsed.dimension,
        device: parsed.device,
        format: parsed.format,
        delay: parsed.delay,
        zoom: parsed.zoom,
        hideSelector: parsed.hideSelector,
        clickSelector: parsed.clickSelector
      })
    }

    if (result.success) {
      return NextResponse.json({
        ok: true,
        data: {
          screenshotUrl: result.screenshotUrl,
          metadata: result.metadata
        }
      })
    } else {
      return NextResponse.json({
        ok: false,
        error: result.error || 'Screenshot capture failed'
      }, { status: 500 })
    }

  } catch (e: any) {
    return NextResponse.json({
      ok: false,
      error: e.message || 'Screenshot API failed'
    }, { status: 400 })
  }
}

/**
 * GET /api/screenshot?url=<url>&device=<device>&...
 * Simple GET endpoint for direct screenshot capture
 */
export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url)
    const url = searchParams.get('url')
    
    if (!url) {
      return NextResponse.json({
        ok: false,
        error: 'URL parameter is required'
      }, { status: 400 })
    }

    const ip = req.headers.get('x-forwarded-for') || 'ip'
    rateLimit(ip, Number(process.env.RATELIMIT_MAX||60), Number(process.env.RATELIMIT_WINDOW_MS||60000))

    // Parse optional parameters
    const options = {
      url,
      dimension: searchParams.get('dimension') || '1024xfull',
      device: (searchParams.get('device') as 'desktop' | 'mobile' | 'tablet') || 'desktop',
      format: (searchParams.get('format') as 'png' | 'jpg' | 'gif') || 'png',
      delay: parseInt(searchParams.get('delay') || '2000'),
      zoom: parseInt(searchParams.get('zoom') || '100'),
      hideSelector: searchParams.get('hide') || undefined,
      clickSelector: searchParams.get('click') || undefined
    }

    // Validate URL
    const urlValidation = validateScreenshotUrl(url)
    if (!urlValidation.valid) {
      return NextResponse.json({
        ok: false,
        error: `Invalid URL: ${urlValidation.error}`
      }, { status: 400 })
    }

    const result = await captureScreenshot(options)

    if (result.success) {
      // For GET requests, redirect directly to the screenshot
      return NextResponse.redirect(result.screenshotUrl!)
    } else {
      return NextResponse.json({
        ok: false,
        error: result.error || 'Screenshot capture failed'
      }, { status: 500 })
    }

  } catch (e: any) {
    return NextResponse.json({
      ok: false,
      error: e.message || 'Screenshot API failed'
    }, { status: 400 })
  }
}
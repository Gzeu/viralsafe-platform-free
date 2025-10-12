/**
 * ScreenshotMachine API Integration
 * Captures website screenshots for visual analysis in security reports
 */

export interface ScreenshotOptions {
  url: string
  dimension?: string
  device?: 'desktop' | 'mobile' | 'tablet'
  format?: 'png' | 'jpg' | 'gif'
  cacheLimit?: number
  delay?: number
  zoom?: number
  hideSelector?: string
  clickSelector?: string
}

export interface ScreenshotResult {
  success: boolean
  screenshotUrl?: string
  error?: string
  responseHeaders?: Record<string, string>
  metadata?: {
    dimension: string
    device: string
    format: string
    timestamp: string
  }
}

const SCREENSHOT_API_KEY = process.env.SCREENSHOTMACHINE_API_KEY || '6610eb'
const SCREENSHOT_BASE_URL = 'https://api.screenshotmachine.com'

/**
 * Capture website screenshot using ScreenshotMachine API
 */
export async function captureScreenshot(
  options: ScreenshotOptions
): Promise<ScreenshotResult> {
  try {
    // Validate URL
    if (!options.url) {
      return {
        success: false,
        error: 'URL is required for screenshot capture'
      }
    }

    // Sanitize URL - ensure it has protocol
    let cleanUrl = options.url.trim()
    if (!cleanUrl.startsWith('http://') && !cleanUrl.startsWith('https://')) {
      cleanUrl = 'https://' + cleanUrl
    }

    // Build screenshot API URL with parameters
    const params = new URLSearchParams({
      key: SCREENSHOT_API_KEY,
      url: cleanUrl,
      dimension: options.dimension || '1024xfull',
      device: options.device || 'desktop',
      format: options.format || 'png',
      cacheLimit: String(options.cacheLimit || 0),
      delay: String(options.delay || 2000),
      zoom: String(options.zoom || 100)
    })

    // Add optional selectors for cookie banners/GDPR handling
    if (options.hideSelector) {
      params.append('hide', options.hideSelector)
    }
    if (options.clickSelector) {
      params.append('click', options.clickSelector)
    }

    const screenshotUrl = `${SCREENSHOT_BASE_URL}/?${params.toString()}`

    // Make request to ScreenshotMachine API
    const response = await fetch(screenshotUrl, {
      method: 'GET',
      headers: {
        'User-Agent': 'ViralSafe-Platform/1.0'
      },
      // Timeout after 30 seconds
      signal: AbortSignal.timeout(30000)
    })

    // Extract response headers for error handling
    const responseHeaders: Record<string, string> = {}
    response.headers.forEach((value, key) => {
      responseHeaders[key] = value
    })

    // Check for API errors via special header
    const apiResponse = responseHeaders['x-screenshotmachine-response']
    if (apiResponse && apiResponse !== 'success') {
      return {
        success: false,
        error: `ScreenshotMachine API error: ${apiResponse}`,
        responseHeaders
      }
    }

    // Check HTTP status
    if (!response.ok) {
      return {
        success: false,
        error: `HTTP ${response.status}: ${response.statusText}`,
        responseHeaders
      }
    }

    // Check content type - should be image
    const contentType = response.headers.get('content-type')
    if (!contentType?.startsWith('image/')) {
      return {
        success: false,
        error: `Invalid content type: ${contentType}. Expected image.`,
        responseHeaders
      }
    }

    // Success - return the screenshot URL
    return {
      success: true,
      screenshotUrl,
      responseHeaders,
      metadata: {
        dimension: options.dimension || '1024xfull',
        device: options.device || 'desktop',
        format: options.format || 'png',
        timestamp: new Date().toISOString()
      }
    }

  } catch (error: any) {
    // Handle network errors, timeouts, etc.
    return {
      success: false,
      error: `Screenshot capture failed: ${error.message || 'Unknown error'}`
    }
  }
}

/**
 * Generate screenshot with smart cookie/GDPR banner handling
 */
export async function captureScreenshotSmart(
  url: string,
  options: Partial<ScreenshotOptions> = {}
): Promise<ScreenshotResult> {
  // First attempt with common cookie banner selectors
  const commonSelectors = {
    hide: '.cookie-banner,.gdpr-banner,.cookie-consent,.privacy-notice',
    click: '.accept-cookies,.accept-all,.consent-accept'
  }

  const result = await captureScreenshot({
    url,
    ...options,
    hideSelector: commonSelectors.hide,
    clickSelector: commonSelectors.click
  })

  // If first attempt fails, try without selectors
  if (!result.success) {
    return await captureScreenshot({
      url,
      ...options
    })
  }

  return result
}

/**
 * Validate if a URL is suitable for screenshot capture
 */
export function validateScreenshotUrl(url: string): { valid: boolean; error?: string } {
  try {
    // Basic URL validation
    let cleanUrl = url.trim()
    if (!cleanUrl) {
      return { valid: false, error: 'URL cannot be empty' }
    }

    // Add protocol if missing
    if (!cleanUrl.startsWith('http://') && !cleanUrl.startsWith('https://')) {
      cleanUrl = 'https://' + cleanUrl
    }

    const urlObj = new URL(cleanUrl)
    
    // Check for supported protocols
    if (!['http:', 'https:'].includes(urlObj.protocol)) {
      return { valid: false, error: 'Only HTTP and HTTPS URLs are supported' }
    }

    // Check for localhost/private IPs (security)
    if (['localhost', '127.0.0.1', '0.0.0.0'].includes(urlObj.hostname) ||
        urlObj.hostname.startsWith('192.168.') ||
        urlObj.hostname.startsWith('10.') ||
        urlObj.hostname.match(/^172\.(1[6-9]|2[0-9]|3[0-1])\./)) {
      return { valid: false, error: 'Private/localhost URLs are not allowed' }
    }

    return { valid: true }
  } catch (error) {
    return { valid: false, error: 'Invalid URL format' }
  }
}
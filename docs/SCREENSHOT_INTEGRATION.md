# 📸 Screenshot Integration - ScreenshotMachine API

## Overview

ViralSafe Platform now includes **visual website analysis** through ScreenshotMachine API integration. Every URL analysis automatically captures a screenshot for enhanced security reporting.

## ✨ Features

- **Automatic Screenshots**: URL analyses include visual captures
- **Smart Cookie Handling**: Automatic GDPR/cookie banner management
- **Multiple Devices**: Desktop, mobile, tablet support
- **Error Handling**: Comprehensive error reporting and fallbacks
- **Rate Limited**: Integrated with platform rate limiting
- **Secure**: URL validation prevents private/localhost access

## 🔧 Configuration

### Environment Variables

```bash
# ScreenshotMachine API Key (default provided)
SCREENSHOTMACHINE_API_KEY=6610eb
```

### Default Settings

```javascript
{
  dimension: '1024xfull',
  device: 'desktop',
  format: 'png',
  delay: 2000,
  zoom: 100,
  cacheLimit: 0
}
```

## 📊 API Endpoints

### 1. Enhanced Analyze Endpoint

**POST** `/api/analyze`

```json
{
  "inputType": "url",
  "url": "https://example.com",
  "includeScreenshot": true,
  "screenshotOptions": {
    "device": "desktop",
    "dimension": "1024xfull",
    "delay": 2000
  }
}
```

**Response with Screenshot:**

```json
{
  "ok": true,
  "data": {
    "id": "analysis_id",
    "risk": { "score": 75, "level": "medium" },
    "screenshot": {
      "success": true,
      "screenshotUrl": "https://api.screenshotmachine.com/?key=...&url=...",
      "metadata": {
        "dimension": "1024xfull",
        "device": "desktop",
        "format": "png",
        "timestamp": "2025-10-13T00:15:00Z"
      }
    }
  }
}
```

### 2. Dedicated Screenshot Endpoint

**POST** `/api/screenshot`

```json
{
  "url": "https://example.com",
  "device": "mobile",
  "dimension": "375x812",
  "format": "png",
  "delay": 3000,
  "zoom": 100,
  "hideSelector": ".cookie-banner",
  "clickSelector": ".accept-cookies"
}
```

**GET** `/api/screenshot?url=https://example.com&device=mobile`

*Direct screenshot redirect - perfect for embedding in img tags*

## 🎯 Usage Examples

### Basic Screenshot Capture

```javascript
const response = await fetch('/api/screenshot', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://suspicious-site.com'
  })
})

const { data } = await response.json()
console.log('Screenshot URL:', data.screenshotUrl)
```

### Enhanced Analysis with Screenshot

```javascript
const analysis = await fetch('/api/analyze', {
  method: 'POST', 
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    inputType: 'url',
    url: 'https://phishing-site.com',
    screenshotOptions: {
      device: 'mobile',
      dimension: '375x812'
    }
  })
})

const result = await analysis.json()
if (result.data.screenshot.success) {
  console.log('Visual evidence captured:', result.data.screenshot.screenshotUrl)
}
```

### Display Screenshot in UI

```jsx
// React component example
function SecurityReport({ analysis }) {
  return (
    <div className="security-report">
      <h3>Risk Assessment: {analysis.risk.level}</h3>
      
      {analysis.screenshot?.success && (
        <div className="visual-evidence">
          <h4>Visual Evidence</h4>
          <img 
            src={analysis.screenshot.screenshotUrl}
            alt="Website Screenshot"
            className="screenshot-preview"
          />
          <p>Captured: {analysis.screenshot.metadata.timestamp}</p>
        </div>
      )}
      
      {analysis.screenshot?.error && (
        <div className="screenshot-error">
          <p>Screenshot unavailable: {analysis.screenshot.error}</p>
        </div>
      )}
    </div>
  )
}
```

## 🛡️ Security Features

### URL Validation

- **Protocol Check**: Only HTTP/HTTPS allowed
- **Private IP Protection**: Blocks localhost, 192.168.x.x, 10.x.x.x, 172.16-31.x.x
- **Format Validation**: Proper URL structure required

### Error Handling

- **API Errors**: X-Screenshotmachine-Response header monitoring
- **Network Timeouts**: 30-second timeout protection
- **Content Validation**: Image content-type verification
- **Graceful Degradation**: Analysis continues if screenshot fails

## 🎨 Device & Format Options

### Devices
- `desktop` - 1024px+ width
- `mobile` - 375px width
- `tablet` - 768px width

### Dimensions
- `1024xfull` - Full page capture
- `1920x1080` - Full HD
- `375x812` - iPhone X/11/12
- `768x1024` - iPad portrait
- Custom: `{width}x{height}` or `{width}xfull`

### Formats
- `png` - Best quality (default)
- `jpg` - Smaller size
- `gif` - Animation support

## 🍪 Cookie Banner Handling

The system automatically handles common GDPR/cookie banners:

### Automatic (Smart Mode)
```javascript
// Automatically applied selectors
hide: '.cookie-banner,.gdpr-banner,.cookie-consent,.privacy-notice'
click: '.accept-cookies,.accept-all,.consent-accept'
```

### Custom Selectors
```javascript
{
  "hideSelector": ".custom-cookie-banner,.modal-overlay",
  "clickSelector": ".btn-accept-cookies"
}
```

## 📈 Integration in Reports

Screenshots enhance security reports by providing:

1. **Visual Evidence**: See actual website appearance
2. **Phishing Detection**: Compare with legitimate sites
3. **UI Analysis**: Identify suspicious design patterns
4. **Brand Verification**: Check for trademark violations
5. **Content Validation**: Visual confirmation of text analysis

## ⚠️ Error Scenarios

### Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid URL format` | Malformed URL | Check URL structure |
| `Private/localhost URLs not allowed` | Security restriction | Use public URLs only |
| `HTTP 4xx/5xx` | Website issues | Check if site is accessible |
| `Invalid content type` | Not an image response | API key or service issue |
| `Screenshot capture failed: timeout` | Slow website | Increase delay parameter |

### Error Response Example

```json
{
  "ok": true,
  "data": {
    "risk": { "score": 80, "level": "high" },
    "screenshot": {
      "success": false,
      "error": "Website timeout after 30 seconds"
    }
  }
}
```

## 🚀 Performance Considerations

- **Parallel Processing**: Screenshots captured alongside AI analysis
- **Rate Limiting**: Shared with main API limits
- **Timeout Protection**: 30-second maximum wait
- **Fallback Strategy**: Analysis continues if screenshot fails
- **Caching**: ScreenshotMachine handles caching automatically

## 🔗 Related Documentation

- [API Documentation](./API.md)
- [Security Features](./SECURITY.md)
- [Deployment Guide](../DEPLOYMENT.md)
- [ScreenshotMachine API Docs](https://screenshotmachine.com/api.php)

---

**Visual security analysis is now an integral part of ViralSafe Platform! 📸🛡️**
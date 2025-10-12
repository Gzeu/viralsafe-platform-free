import { fetchVerdict, scanUrl } from './virustotal'

interface URLIntelligence {
  domain: string
  reputation: 'trusted' | 'suspicious' | 'malicious' | 'unknown'
  riskScore: number
  analysis: {
    domainAge: number | null
    isShortener: boolean
    hasRedirects: boolean
    usesHTTPS: boolean
    certificateValid: boolean
    suspiciousTLD: boolean
  }
  threatCategories: string[]
  vtResults?: {
    verdict: string
    stats: any
    scanId: string
  }
}

// Suspicious TLDs commonly used in scams
const SUSPICIOUS_TLDS = [
  '.tk', '.ml', '.ga', '.cf', '.top', '.click', '.download', '.stream',
  '.science', '.racing', '.party', '.review', '.country', '.cricket',
  '.accountant', '.loan', '.men', '.win', '.date', '.faith'
]

// Known URL shorteners and suspicious domains
const URL_SHORTENERS = [
  'bit.ly', 'tinyurl.com', 'short.gy', 'rebrand.ly', 'ow.ly', 
  't.co', 'goo.gl', 'cutt.ly', '2no.co', 'grabify.link',
  'iplogger.org', 'discord.gg', 'telegram.me'
]

// Trusted domains (whitelist)
const TRUSTED_DOMAINS = [
  'google.com', 'microsoft.com', 'apple.com', 'amazon.com',
  'facebook.com', 'twitter.com', 'linkedin.com', 'github.com',
  'stackoverflow.com', 'wikipedia.org', 'youtube.com', 'reddit.com'
]

export class URLIntelligenceAnalyzer {
  private static extractDomain(url: string): string {
    try {
      const parsed = new URL(url.startsWith('http') ? url : `https://${url}`)
      return parsed.hostname.toLowerCase().replace(/^www\./, '')
    } catch {
      return url.toLowerCase()
    }
  }
  
  private static analyzeDomainReputation(domain: string): { reputation: URLIntelligence['reputation']; score: number } {
    // Check trusted domains
    if (TRUSTED_DOMAINS.some(trusted => domain === trusted || domain.endsWith('.' + trusted))) {
      return { reputation: 'trusted', score: 5 }
    }
    
    // Check URL shorteners
    if (URL_SHORTENERS.includes(domain)) {
      return { reputation: 'suspicious', score: 40 }
    }
    
    // Check suspicious TLDs
    if (SUSPICIOUS_TLDS.some(tld => domain.endsWith(tld))) {
      return { reputation: 'suspicious', score: 35 }
    }
    
    // Check for suspicious patterns
    let suspicionScore = 0
    
    // Long subdomains (often used in phishing)
    const subdomains = domain.split('.')
    if (subdomains.length > 3) suspicionScore += 15
    
    // Numbers in domain (suspicious pattern)
    if (/\d{3,}/.test(domain)) suspicionScore += 10
    
    // Homograph attacks (similar looking characters)
    if (/[а-я]|[α-ω]/.test(domain)) suspicionScore += 25
    
    // Multiple hyphens
    if ((domain.match(/-/g) || []).length >= 3) suspicionScore += 10
    
    // Brand impersonation patterns
    const brandPatterns = [
      /paypal|amazon|google|microsoft|apple|facebook|twitter|instagram/,
      /bank|secure|login|verify|update|confirm/,
      /crypto|bitcoin|ethereum|binance|coinbase/
    ]
    
    brandPatterns.forEach(pattern => {
      if (pattern.test(domain) && !TRUSTED_DOMAINS.includes(domain)) {
        suspicionScore += 20
      }
    })
    
    if (suspicionScore >= 40) return { reputation: 'malicious', score: suspicionScore + 20 }
    if (suspicionScore >= 20) return { reputation: 'suspicious', score: suspicionScore }
    return { reputation: 'unknown', score: suspicionScore }
  }
  
  private static analyzeURL(url: string): Omit<URLIntelligence, 'vtResults'> {
    const domain = this.extractDomain(url)
    const { reputation, score } = this.analyzeDomainReputation(domain)
    
    const analysis = {
      domainAge: null, // Would need external API for real domain age
      isShortener: URL_SHORTENERS.includes(domain),
      hasRedirects: false, // Would need to follow redirects to detect
      usesHTTPS: url.startsWith('https://'),
      certificateValid: true, // Would need certificate validation
      suspiciousTLD: SUSPICIOUS_TLDS.some(tld => domain.endsWith(tld))
    }
    
    const threatCategories: string[] = []
    if (analysis.isShortener) threatCategories.push('url_shortener')
    if (analysis.suspiciousTLD) threatCategories.push('suspicious_tld')
    if (!analysis.usesHTTPS) threatCategories.push('insecure_connection')
    if (reputation === 'malicious') threatCategories.push('known_malicious')
    if (reputation === 'suspicious') threatCategories.push('suspicious_domain')
    
    // Adjust risk score based on analysis
    let riskScore = score
    if (!analysis.usesHTTPS) riskScore += 15
    if (analysis.isShortener) riskScore += 25
    if (analysis.suspiciousTLD) riskScore += 20
    
    return {
      domain,
      reputation,
      riskScore: Math.min(riskScore, 95),
      analysis,
      threatCategories
    }
  }
  
  public static async comprehensiveURLAnalysis(url: string): Promise<URLIntelligence> {
    const baseAnalysis = this.analyzeURL(url)
    
    // Try to get VirusTotal results
    let vtResults
    try {
      if (process.env.VIRUSTOTAL_API_KEY) {
        const { id } = await scanUrl(url)
        
        // Wait a bit for analysis
        await new Promise(resolve => setTimeout(resolve, 3000))
        
        const verdict = await fetchVerdict(id)
        vtResults = {
          verdict: verdict.verdict,
          stats: verdict.stats,
          scanId: id
        }
        
        // Adjust risk score based on VT results
        if (verdict.verdict === 'malicious') {
          baseAnalysis.riskScore = Math.max(baseAnalysis.riskScore, 85)
          baseAnalysis.reputation = 'malicious'
          baseAnalysis.threatCategories.push('virustotal_malicious')
        }
      }
    } catch (error) {
      console.warn('VirusTotal analysis failed:', error)
    }
    
    return {
      ...baseAnalysis,
      vtResults
    }
  }
}
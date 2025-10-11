const VT_API_KEY = process.env.VIRUSTOTAL_API_KEY
const VT_BASE = 'https://www.virustotal.com/api/v3'

export interface VTScanResult {
  id: string
  verdict: 'harmless' | 'malicious' | 'suspicious' | 'pending' | 'timeout'
  stats: {
    harmless: number
    malicious: number
    suspicious: number
    undetected: number
    timeout: number
  }
}

export async function submitUrlScan(url: string): Promise<{ id: string }> {
  if (!VT_API_KEY) {
    throw new Error('VirusTotal API key not configured')
  }

  const response = await fetch(`${VT_BASE}/urls`, {
    method: 'POST',
    headers: {
      'x-apikey': VT_API_KEY,
      'content-type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({ url })
  })

  if (!response.ok) {
    throw new Error(`VirusTotal failed: ${response.status}`)
  }

  const data = await response.json()
  return { id: data.data.id }
}

export async function getAnalysisResult(id: string): Promise<VTScanResult> {
  const response = await fetch(`${VT_BASE}/analyses/${id}`, {
    headers: { 'x-apikey': VT_API_KEY! }
  })

  if (!response.ok) {
    throw new Error(`VirusTotal analysis failed: ${response.status}`)
  }

  const data = await response.json()
  const stats = data.data.attributes.stats || {}
  
  const malicious = stats.malicious || 0
  const suspicious = stats.suspicious || 0
  const harmless = stats.harmless || 0
  
  let verdict: VTScanResult['verdict']
  if (malicious >= 2) verdict = 'malicious'
  else if (malicious >= 1 || suspicious >= 3) verdict = 'suspicious'
  else if (harmless >= 1) verdict = 'harmless'
  else verdict = 'pending'

  return {
    id,
    verdict,
    stats: {
      harmless: stats.harmless || 0,
      malicious: stats.malicious || 0,
      suspicious: stats.suspicious || 0,
      undetected: stats.undetected || 0,
      timeout: stats.timeout || 0
    }
  }
}
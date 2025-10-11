const VT_KEY = process.env.VIRUSTOTAL_API_KEY
const VT_BASE = 'https://www.virustotal.com/api/v3'

export async function scanUrl(url: string) {
  if (!VT_KEY) throw new Error('VIRUSTOTAL_API_KEY missing')
  
  const resp = await fetch(`${VT_BASE}/urls`, {
    method: 'POST',
    headers: { 'x-apikey': VT_KEY, 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ url }),
    cache: 'no-store',
  })
  
  if (!resp.ok) throw new Error('VirusTotal submission failed')
  const data = await resp.json()
  return { id: data.data.id as string }
}

export async function fetchVerdict(id: string) {
  if (!VT_KEY) throw new Error('VIRUSTOTAL_API_KEY missing')
  
  const r = await fetch(`${VT_BASE}/analyses/${id}`, { headers: { 'x-apikey': VT_KEY }, cache: 'no-store' })
  if (!r.ok) throw new Error('VirusTotal analysis fetch failed')
  
  const d = await r.json()
  const stats = d.data.attributes.stats
  const malicious = stats.malicious || 0
  const suspicious = stats.suspicious || 0
  const harmless = stats.harmless || 0
  
  const verdict = malicious + suspicious > harmless ? 'malicious' : 'harmless'
  return { verdict, stats }
}
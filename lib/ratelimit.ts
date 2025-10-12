const hits = new Map<string, { count: number; ts: number }>()

export function rateLimit(ip: string, max: number, windowMs: number) {
  const now = Date.now()
  const entry = hits.get(ip) || { count: 0, ts: now }
  
  if (now - entry.ts > windowMs) { entry.count = 0; entry.ts = now }
  entry.count++
  hits.set(ip, entry)
  
  if (entry.count > max) throw new Error('Rate limit exceeded')
}
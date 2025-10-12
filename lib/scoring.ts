export type Risk = { score: number; level: 'low'|'medium'|'high'; reasons: string[] }

export function computeRisk(input: { aiScore?: number; flags: string[]; url?: string; platform?: string }): Risk {
  let score = 0
  const reasons: string[] = []
  
  if (input.aiScore != null) { score += input.aiScore; reasons.push('AI classification') }
  if (input.url && /bit.ly|tinyurl|grabify|iplogger/i.test(input.url)) { score += 25; reasons.push('Suspicious/shortened domain') }
  if (input.flags.includes('phishing')) { score += 35; reasons.push('Phishing indicators') }
  if (input.flags.includes('malware')) { score += 45; reasons.push('Potential malware reference') }
  if (input.platform && /whatsapp|telegram/i.test(input.platform)) { score += 5; reasons.push('High-abuse platform') }
  
  score = Math.max(0, Math.min(100, score))
  const level = score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low'
  
  return { score, level, reasons }
}
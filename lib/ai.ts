type AIResult = { aiScore: number; flags: string[]; provider: string }

async function tryProvider(name: string, fn: (()=>Promise<AIResult>) | null): Promise<AIResult | null> {
  if (!fn) return null
  try { const r = await fn(); return { ...r, provider: name } } catch { return null }
}

export async function classifyText(text: string): Promise<AIResult> {
  const hasOpenAI = !!process.env.OPENAI_API_KEY
  const hasGroq = !!process.env.GROQ_API_KEY
  const hasGemini = !!process.env.GEMINI_API_KEY
  
  const providers: Array<Promise<AIResult | null>> = []
  
  // Adaugă aici integrarea reală dacă vrei; momentan păstrăm fallback-urile.
  if (hasGroq) providers.push(tryProvider('groq', null))
  if (hasOpenAI) providers.push(tryProvider('openai', null))
  if (hasGemini) providers.push(tryProvider('gemini', null))
  
  for (const p of providers) {
    const res = await p
    if (res) return res
  }
  
  // Fallback euristic
  const flags: string[] = []
  if (/free\s+crypto|airdrop|seed\sphrase|private\skey|2fa\s+reset|urgent\s+verify/i.test(text)) flags.push('phishing')
  if (/download\s+exe|apk|crack|keygen/i.test(text)) flags.push('malware')
  
  const base = flags.includes('malware') ? 60 : flags.includes('phishing') ? 55 : 15
  return { aiScore: base, flags, provider: 'heuristics' }
}
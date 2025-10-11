import { z } from 'zod'

export const analyzeSchema = z.object({
  inputType: z.enum(['text','url']),
  platform: z.string().default('general').optional(),
  content: z.string().max(5000).optional(),
  url: z.string().url().optional(),
})

export const scanSchema = z.object({ url: z.string().url() })
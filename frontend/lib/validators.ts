import { z } from 'zod'

export const analyzeSchema = z.object({
  inputType: z.enum(['text', 'url']),
  platform: z.string().default('general'),
  content: z.string().max(5000).optional(),
  url: z.string().url().optional(),
  checkUrls: z.boolean().default(true),
  userAgent: z.string().optional()
}).refine(
  (data) => {
    if (data.inputType === 'text' && !data.content?.trim()) {
      return false
    }
    if (data.inputType === 'url' && !data.url?.trim()) {
      return false
    }
    return true
  },
  {
    message: 'Content is required for text analysis, URL is required for URL analysis'
  }
)

export const scanSchema = z.object({
  url: z.string().url('Invalid URL format'),
  deepScan: z.boolean().default(false),
  waitForResults: z.boolean().default(true)
})

export const batchAnalyzeSchema = z.object({
  items: z.array(z.object({
    inputType: z.enum(['text', 'url']),
    content: z.string().max(5000).optional(),
    url: z.string().url().optional(),
    platform: z.string().default('general')
  })).max(10), // Limit batch size
  parallel: z.boolean().default(true)
})

export type AnalyzeInput = z.infer<typeof analyzeSchema>
export type ScanInput = z.infer<typeof scanSchema>
export type BatchAnalyzeInput = z.infer<typeof batchAnalyzeSchema>
import { z } from 'zod'

export const analyzeSchema = z.object({
  inputType: z.enum(['text','url']),
  platform: z.string().default('general').optional(),
  content: z.string().max(5000).optional(),
  url: z.string().url().optional(),
  // Screenshot options
  includeScreenshot: z.boolean().default(true).optional(),
  screenshotOptions: z.object({
    dimension: z.string().default('1024xfull').optional(),
    device: z.enum(['desktop', 'mobile', 'tablet']).default('desktop').optional(),
    format: z.enum(['png', 'jpg', 'gif']).default('png').optional(),
    delay: z.number().min(1000).max(10000).default(2000).optional(),
    zoom: z.number().min(50).max(200).default(100).optional()
  }).optional()
})

export const scanSchema = z.object({ url: z.string().url() })

export const screenshotSchema = z.object({
  url: z.string().url(),
  dimension: z.string().default('1024xfull').optional(),
  device: z.enum(['desktop', 'mobile', 'tablet']).default('desktop').optional(),
  format: z.enum(['png', 'jpg', 'gif']).default('png').optional(),
  delay: z.number().min(1000).max(10000).default(2000).optional(),
  zoom: z.number().min(50).max(200).default(100).optional(),
  hideSelector: z.string().optional(),
  clickSelector: z.string().optional()
})
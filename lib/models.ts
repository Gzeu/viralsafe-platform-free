import { Schema, model, models } from 'mongoose'

const AnalysisSchema = new Schema({
  inputType: { type: String, enum: ['text','url'], required: true },
  platform: { type: String, default: 'general' },
  content: String,
  url: String,
  provider: String,
  risk: { score: Number, level: String, reasons: [String] },
  tags: [String],
  // Screenshot-related fields
  screenshot: {
    success: { type: Boolean, default: false },
    screenshotUrl: String,
    error: String,
    metadata: {
      dimension: String,
      device: String,
      format: String,
      timestamp: String
    }
  },
  createdAt: { type: Date, default: Date.now },
})

const ScanSchema = new Schema({
  url: String,
  vtScanId: String,
  vtVerdict: String,
  risk: { score: Number, level: String },
  createdAt: { type: Date, default: Date.now },
})

export const Analysis = models.Analysis || model('Analysis', AnalysisSchema)
export const Scan = models.Scan || model('Scan', ScanSchema)
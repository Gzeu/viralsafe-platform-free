import { Schema, model, models } from 'mongoose'

const AnalysisSchema = new Schema({
  inputType: { 
    type: String, 
    enum: ['text', 'url'], 
    required: true 
  },
  platform: { 
    type: String, 
    default: 'general',
    enum: ['general', 'twitter', 'facebook', 'telegram', 'whatsapp', 'instagram', 'tiktok', 'linkedin', 'email', 'sms']
  },
  content: {
    type: String,
    maxlength: 5000
  },
  url: {
    type: String,
    validate: {
      validator: function(v: string) {
        if (!v) return true
        return /^https?:\/\/.+/.test(v)
      },
      message: 'Invalid URL format'
    }
  },
  provider: {
    type: String,
    enum: ['groq', 'openai', 'gemini', 'heuristics'],
    required: true
  },
  risk: {
    score: {
      type: Number,
      min: 0,
      max: 100,
      required: true
    },
    level: {
      type: String,
      enum: ['low', 'medium', 'high'],
      required: true
    },
    reasons: [{
      type: String,
      maxlength: 200
    }]
  },
  tags: [{
    type: String,
    maxlength: 50
  }],
  processingTimeMs: {
    type: Number,
    default: 0
  },
  userAgent: String,
  ipHash: String
}, {
  timestamps: true
})

const ScanSchema = new Schema({
  url: {
    type: String,
    required: true,
    validate: {
      validator: function(v: string) {
        return /^https?:\/\/.+/.test(v)
      },
      message: 'Invalid URL format'
    }
  },
  vtScanId: {
    type: String,
    required: true
  },
  vtVerdict: {
    type: String,
    enum: ['harmless', 'malicious', 'suspicious', 'pending', 'timeout'],
    default: 'pending'
  },
  vtStats: {
    harmless: { type: Number, default: 0 },
    malicious: { type: Number, default: 0 },
    suspicious: { type: Number, default: 0 },
    undetected: { type: Number, default: 0 },
    timeout: { type: Number, default: 0 }
  },
  risk: {
    score: {
      type: Number,
      min: 0,
      max: 100,
      required: true
    },
    level: {
      type: String,
      enum: ['low', 'medium', 'high'],
      required: true
    }
  },
  processingTimeMs: {
    type: Number,
    default: 0
  },
  ipHash: String
}, {
  timestamps: true
})

// Create indexes for performance
AnalysisSchema.index({ createdAt: -1 })
AnalysisSchema.index({ 'risk.level': 1 })
AnalysisSchema.index({ platform: 1 })
ScanSchema.index({ createdAt: -1 })
ScanSchema.index({ vtVerdict: 1 })

export const Analysis = models.Analysis || model('Analysis', AnalysisSchema)
export const Scan = models.Scan || model('Scan', ScanSchema)
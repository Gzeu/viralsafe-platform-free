import { NextResponse } from 'next/server'
import { dbConnect } from '@/lib/db'
import { Analysis, Scan } from '@/lib/models'

export async function GET() {
  try {
    await dbConnect()
    
    // Get basic counts
    const [totalAnalyses, totalScans] = await Promise.all([
      Analysis.countDocuments({}),
      Scan.countDocuments({})
    ])
    
    // Risk distribution
    const [highRisk, mediumRisk, lowRisk] = await Promise.all([
      Analysis.countDocuments({ 'risk.level': 'high' }),
      Analysis.countDocuments({ 'risk.level': 'medium' }),
      Analysis.countDocuments({ 'risk.level': 'low' })
    ])
    
    // Platform distribution
    const platformStats = await Analysis.aggregate([
      {
        $group: {
          _id: '$platform',
          count: { $sum: 1 }
        }
      },
      {
        $project: {
          _id: 0,
          platform: '$_id',
          count: 1
        }
      }
    ])
    
    const platformDistribution = platformStats.reduce((acc, item) => {
      acc[item.platform] = item.count
      return acc
    }, {} as Record<string, number>)
    
    // Provider performance
    const providerStats = await Analysis.aggregate([
      {
        $group: {
          _id: '$provider',
          count: { $sum: 1 },
          avgScore: { $avg: '$risk.score' },
          avgProcessingTime: { $avg: '$processingTimeMs' }
        }
      }
    ])
    
    const providerPerformance = providerStats.reduce((acc, item) => {
      acc[item._id] = {
        count: item.count,
        avgScore: Math.round((item.avgScore || 0) * 10) / 10,
        avgProcessingTimeMs: Math.round(item.avgProcessingTime || 0)
      }
      return acc
    }, {} as Record<string, any>)
    
    // Recent activity (last 24 hours)
    const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000)
    const recentAnalyses = await Analysis.countDocuments({ 
      createdAt: { $gte: yesterday } 
    })
    
    // Average risk score
    const avgRiskResult = await Analysis.aggregate([
      {
        $group: {
          _id: null,
          avgRiskScore: { $avg: '$risk.score' }
        }
      }
    ])
    
    const avgRiskScore = avgRiskResult[0]?.avgRiskScore || 0
    
    // Top threat categories
    const threatCategories = await Analysis.aggregate([
      { $unwind: '$tags' },
      {
        $group: {
          _id: '$tags',
          count: { $sum: 1 }
        }
      },
      { $sort: { count: -1 } },
      { $limit: 10 }
    ])
    
    const topThreats = threatCategories.reduce((acc, item) => {
      acc[item._id] = item.count
      return acc
    }, {} as Record<string, number>)
    
    // Database status
    const dbStatus = mongoose.connection.readyState === 1 ? 'connected' : 'disconnected'
    
    const analyticsData = {
      ok: true,
      total_analyses: totalAnalyses,
      total_scans: totalScans,
      recent_analyses_24h: recentAnalyses,
      risk_distribution: {
        high: highRisk,
        medium: mediumRisk,
        low: lowRisk
      },
      platform_stats: platformDistribution,
      provider_performance: providerPerformance,
      avg_risk_score: avgRiskScore / 100, // Convert to 0-1 scale
      top_threat_categories: topThreats,
      database_status: dbStatus,
      generated_at: new Date().toISOString(),
      uptime_seconds: Math.floor(process.uptime())
    }
    
    return NextResponse.json(analyticsData)
    
  } catch (error: any) {
    console.error('Analytics failed:', error)
    
    return NextResponse.json({
      ok: false,
      error: error.message || 'Analytics generation failed',
      total_analyses: 0,
      risk_distribution: { high: 0, medium: 0, low: 0 },
      platform_stats: {},
      avg_risk_score: 0,
      database_status: 'error',
      generated_at: new Date().toISOString()
    }, { status: 500 })
  }
}
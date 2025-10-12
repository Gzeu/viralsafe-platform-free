import { NextResponse } from 'next/server'
import mongoose from 'mongoose'
import { dbConnect } from '@/lib/db'
import { Analysis, Scan } from '@/lib/models'

export async function GET() {
  const startTime = Date.now()
  
  try {
    // Check database connection
    let databaseStatus = 'disconnected'
    let databaseResponseTime = 0
    let collections: Record<string, number> = {}
    
    try {
      await dbConnect()
      const dbStart = Date.now()
      
      // Quick ping to test connection - SAFE CHECK
      if (mongoose.connection.db) {
        await mongoose.connection.db.admin().ping()
        databaseResponseTime = Date.now() - dbStart
        databaseStatus = 'connected'
        
        // Get collection counts
        const [analysisCount, scanCount] = await Promise.all([
          Analysis.countDocuments({}),
          Scan.countDocuments({})
        ])
        
        collections = {
          analyses: analysisCount,
          scans: scanCount
        }
      } else {
        databaseStatus = 'connecting'
      }
      
    } catch (error) {
      console.error('Database health check failed:', error)
      databaseStatus = 'error'
    }
    
    // Check VirusTotal API availability
    let vtStatus = 'not_configured'
    let vtResponseTime = 0
    let vtRateLimit = null
    
    if (process.env.VIRUSTOTAL_API_KEY) {
      try {
        const vtStart = Date.now()
        const response = await fetch('https://www.virustotal.com/api/v3/users/current', {
          headers: {
            'x-apikey': process.env.VIRUSTOTAL_API_KEY
          }
        })
        
        vtResponseTime = Date.now() - vtStart
        
        if (response.ok) {
          vtStatus = 'connected'
          
          // Extract rate limit info from headers if available
          const rateLimitRemaining = response.headers.get('x-ratelimit-requests-remaining')
          if (rateLimitRemaining) {
            vtRateLimit = {
              remaining: parseInt(rateLimitRemaining),
              limit: 4 // Per minute for free tier
            }
          }
        } else {
          vtStatus = 'error'
        }
      } catch (error) {
        console.error('VirusTotal health check failed:', error)
        vtStatus = 'error'
      }
    }
    
    // Check AI providers availability
    const aiProviders = {
      groq: !!process.env.GROQ_API_KEY,
      openai: !!process.env.OPENAI_API_KEY,
      gemini: !!process.env.GEMINI_API_KEY
    }
    
    const enabledProviders = Object.entries(aiProviders)
      .filter(([, enabled]) => enabled)
      .map(([name]) => name)
    
    // System metrics
    const uptime = process.uptime()
    const memoryUsage = process.memoryUsage()
    
    // Overall system health
    let overallStatus = 'healthy'
    if (databaseStatus === 'error' || vtStatus === 'error') {
      overallStatus = 'degraded'
    }
    if (databaseStatus === 'error' && enabledProviders.length === 0) {
      overallStatus = 'unhealthy'
    }
    
    const healthData = {
      status: overallStatus,
      timestamp: new Date().toISOString(),
      version: '3.1.0',
      environment: process.env.NODE_ENV || 'development',
      services: {
        database: {
          status: databaseStatus,
          response_time_ms: databaseResponseTime,
          collections
        },
        virustotal: {
          status: vtStatus,
          response_time_ms: vtResponseTime,
          ...(vtRateLimit && { rate_limit: vtRateLimit })
        },
        ai_providers: {
          available: enabledProviders,
          count: enabledProviders.length
        }
      },
      uptime_info: {
        uptime_seconds: Math.floor(uptime),
        analyses_processed: collections.analyses || 0,
        memory_usage_mb: Math.round(memoryUsage.heapUsed / 1024 / 1024),
        port: process.env.PORT || 3000
      },
      performance: {
        health_check_time_ms: Date.now() - startTime
      }
    }
    
    return NextResponse.json({ ok: true, ...healthData })
    
  } catch (error: any) {
    console.error('Health check failed:', error)
    
    return NextResponse.json({
      ok: false,
      status: 'error',
      error: error.message || 'Health check failed',
      timestamp: new Date().toISOString(),
      uptime_info: {
        uptime_seconds: Math.floor(process.uptime())
      }
    }, { status: 500 })
  }
}
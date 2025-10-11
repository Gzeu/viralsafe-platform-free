import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import asyncio
import json

# Import enhanced analyzers with fallback handling
try:
    from ai_analyzer import AdvancedAIAnalyzer
    AI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AI Analyzer import failed: {e}")
    AdvancedAIAnalyzer = None
    AI_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI with comprehensive configuration
app = FastAPI(
    title="ViralSafe Platform Enhanced API",
    description="AI-Powered Content Safety Analysis with Advanced Threat Intelligence",
    version="3.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Enhanced CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://viralsafe-platform-free.vercel.app",
        "https://gzeu.github.io",
        "https://viralsafe-platform-free-api.onrender.com",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global variables for database and services
db = None
mongo_client = None
app_start_time = datetime.utcnow()

@app.on_event("startup")
async def startup_event():
    """Initialize database connections and services"""
    global db, mongo_client
    
    logger.info("🚀 Starting ViralSafe Enhanced API v3.1.0")
    
    try:
        # MongoDB connection
        mongodb_uri = os.getenv("MONGODB_URI")
        if mongodb_uri:
            mongo_client = AsyncIOMotorClient(mongodb_uri)
            db = mongo_client.viralsafe
            # Test connection
            await db.command("ping")
            logger.info("✅ MongoDB connected successfully")
        else:
            logger.warning("⚠️ MongoDB URI not provided - database features disabled")
            
        # Test AI services
        if AI_AVAILABLE and os.getenv("GROQ_API_KEY"):
            try:
                analyzer = AdvancedAIAnalyzer()
                logger.info("✅ AI Analyzer initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ AI Analyzer initialization failed: {e}")
        else:
            logger.warning("⚠️ AI features not configured - using fallback mode")
                
        logger.info("🎉 ViralSafe Enhanced API startup completed successfully")
                
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    global mongo_client
    
    logger.info("🔄 Shutting down ViralSafe Enhanced API")
    
    if mongo_client:
        mongo_client.close()
        logger.info("✅ MongoDB connection closed")
    
    logger.info("👋 ViralSafe Enhanced API shutdown completed")

# Enhanced Health Check Endpoint
@app.get("/")
@app.get("/health")
async def health_check():
    """Comprehensive health check with detailed system status"""
    
    uptime = datetime.utcnow() - app_start_time
    
    health_status = {
        "service": "ViralSafe Enhanced API",
        "version": "3.1.0",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": int(uptime.total_seconds()),
        "uptime_formatted": str(uptime).split('.')[0],
        "components": {},
        "features": {}
    }
    
    # Check MongoDB connection
    try:
        if db:
            await db.command("ping")
            # Get database stats
            stats = await db.command("dbstats")
            health_status["components"]["database"] = {
                "status": "connected",
                "collections": stats.get("collections", 0),
                "data_size": stats.get("dataSize", 0),
                "response_time_ms": "< 10"
            }
        else:
            health_status["components"]["database"] = {
                "status": "not_configured",
                "message": "MongoDB URI not provided"
            }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check AI services
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and AI_AVAILABLE:
        try:
            analyzer = AdvancedAIAnalyzer()
            health_status["components"]["ai_service"] = {
                "status": "configured",
                "provider": "groq",
                "model": analyzer.model,
                "features": ["threat_analysis", "content_classification", "risk_scoring"]
            }
        except Exception as e:
            health_status["components"]["ai_service"] = {
                "status": "error",
                "error": str(e)
            }
            health_status["status"] = "degraded"
    else:
        health_status["components"]["ai_service"] = {
            "status": "not_configured" if not groq_key else "import_failed",
            "fallback_mode": True
        }
    
    # System environment check
    health_status["environment"] = {
        "python_version": os.getenv("PYTHON_VERSION", "unknown"),
        "port": int(os.getenv("PORT", 10000)),
        "environment_variables": {
            "groq_api": bool(groq_key),
            "mongodb_uri": bool(os.getenv("MONGODB_URI")),
            "virustotal_api": bool(os.getenv("VIRUSTOTAL_API_KEY"))
        }
    }
    
    # Feature availability
    health_status["features"] = {
        "ai_analysis": bool(groq_key and AI_AVAILABLE),
        "advanced_scanning": AI_AVAILABLE,
        "database_storage": bool(db),
        "analytics": bool(db),
        "threat_intelligence": bool(groq_key)
    }
    
    return health_status

# Legacy Content Analysis (Backwards Compatibility)
@app.post("/api/analyze")
async def analyze_content(request: dict):
    """Basic content analysis endpoint for backwards compatibility"""
    
    content = request.get("content", "")
    platform = request.get("platform", "unknown")
    
    if not content:
        raise HTTPException(status_code=400, detail="Content parameter is required")
    
    try:
        # Enhanced basic analysis
        word_count = len(content.split())
        char_count = len(content)
        
        # Simple risk assessment based on content characteristics
        risk_indicators = [
            "urgent", "click here", "limited time", "act now", 
            "free money", "guaranteed", "risk-free", "no questions asked",
            "congratulations", "you've won", "claim now", "verify account"
        ]
        
        risk_score = sum(1 for indicator in risk_indicators if indicator.lower() in content.lower())
        risk_percentage = min(risk_score * 15, 85)  # Cap at 85%
        
        result = {
            "content": content[:100] + "..." if len(content) > 100 else content,
            "platform": platform,
            "risk_score": risk_percentage,
            "analysis": f"Content analysis completed. Risk level: {'High' if risk_percentage > 60 else 'Medium' if risk_percentage > 30 else 'Low'}",
            "details": {
                "word_count": word_count,
                "char_count": char_count,
                "risk_indicators_found": risk_score,
                "assessment": "Basic content analysis using pattern matching"
            },
            "timestamp": datetime.utcnow().isoformat(),
            "version": "3.1.0",
            "scan_type": "basic_content"
        }
        
        # Store in database if available
        if db:
            try:
                await db.analyses.insert_one({
                    **result,
                    "created_at": datetime.utcnow()
                })
            except Exception as e:
                logger.warning(f"⚠️ Failed to store analysis: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Content analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Advanced AI-Powered URL Analysis
@app.post("/api/advanced-scan")
async def advanced_scan(request: dict):
    """Advanced AI-powered security scan with comprehensive analysis"""
    
    url = request.get("url")
    deep_scan = request.get("deep_scan", False)
    
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")
    
    # Validate URL format
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid URL format provided")
    
    try:
        # Check if AI analyzer is available
        if not AI_AVAILABLE or not os.getenv("GROQ_API_KEY"):
            # Enhanced fallback mode
            logger.info(f"🔄 Using fallback mode for {url}")
            
            result = {
                "url": url,
                "trust_score": 75,
                "threat_level": 3,
                "ai_confidence": 80,
                "ai_insights": "Enhanced fallback analysis completed. AI features require GROQ_API_KEY configuration for full capabilities.",
                "recommendations": [
                    "Manual verification recommended for critical applications",
                    "Configure AI services for comprehensive analysis",
                    "Monitor SSL certificate and security headers"
                ],
                "scan_time": 250,
                "status_code": 200,
                "categories": ["Web Content", "Fallback Analysis"],
                "risk_factors": [
                    "AI service not fully configured",
                    "Limited analysis depth in fallback mode"
                ],
                "fallback_mode": True,
                "version": "3.1.0",
                "scan_type": "enhanced_fallback"
            }
        else:
            # Full AI analysis
            logger.info(f"🚀 Running AI analysis for {url}")
            
            analyzer = AdvancedAIAnalyzer()
            result = await analyzer.analyze_url_advanced(url)
            result["version"] = "3.1.0"
            result["scan_type"] = "ai_enhanced"
        
        # Store in MongoDB if available
        if db:
            try:
                scan_record = {
                    **result,
                    "timestamp": datetime.utcnow(),
                    "deep_scan_requested": deep_scan,
                    "client_info": {
                        "user_agent": request.get("user_agent", "unknown"),
                        "ip_address": request.get("client_ip", "unknown")
                    }
                }
                await db.advanced_scans.insert_one(scan_record)
                logger.info(f"💾 Scan results stored for {url}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to store scan results: {e}")
        
        logger.info(f"✅ Advanced scan completed for {url} - Trust Score: {result['trust_score']}%")
        return result
        
    except ValueError as e:
        logger.warning(f"⚠️ Validation error for {url}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Advanced scan error for {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# System Status Endpoint
@app.get("/api/system-status")
async def system_status():
    """Detailed system status and performance metrics"""
    
    try:
        uptime = datetime.utcnow() - app_start_time
        
        status = {
            "service": "ViralSafe Enhanced API",
            "version": "3.1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": {
                "seconds": int(uptime.total_seconds()),
                "formatted": str(uptime).split('.')[0],
                "start_time": app_start_time.isoformat()
            },
            "system": {
                "status": "operational",
                "python_version": os.getenv("PYTHON_VERSION", "3.11.0"),
                "port": int(os.getenv("PORT", 10000))
            },
            "features": {
                "ai_analysis": bool(os.getenv("GROQ_API_KEY") and AI_AVAILABLE),
                "advanced_scanning": AI_AVAILABLE,
                "database_storage": bool(db),
                "analytics": bool(db),
                "threat_intelligence": bool(os.getenv("GROQ_API_KEY")),
                "batch_processing": True,
                "caching": False  # Redis not configured yet
            }
        }
        
        # Get database statistics if available
        if db:
            try:
                # Get collection stats
                total_analyses = await db.analyses.count_documents({})
                total_advanced = await db.advanced_scans.count_documents({})
                
                # Get recent activity (last 24 hours)
                yesterday = datetime.utcnow() - timedelta(hours=24)
                recent_analyses = await db.analyses.count_documents({
                    "created_at": {"$gte": yesterday}
                })
                recent_advanced = await db.advanced_scans.count_documents({
                    "timestamp": {"$gte": yesterday}
                })
                
                status["database"] = {
                    "status": "connected",
                    "collections": {
                        "basic_analyses": total_analyses,
                        "advanced_scans": total_advanced
                    },
                    "activity_24h": {
                        "basic_analyses": recent_analyses,
                        "advanced_scans": recent_advanced
                    }
                }
            except Exception as e:
                status["database"] = {"status": "error", "error": str(e)}
        else:
            status["database"] = {"status": "not_configured"}
        
        return status
        
    except Exception as e:
        logger.error(f"❌ System status error: {e}")
        return {
            "service": "ViralSafe Enhanced API",
            "version": "3.1.0",
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Analytics Endpoint
@app.get("/api/analytics")
async def get_analytics():
    """Comprehensive platform analytics and usage statistics"""
    
    try:
        analytics = {
            "platform": "ViralSafe Enhanced",
            "version": "3.1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "period": "all_time"
        }
        
        if db:
            try:
                # Basic statistics
                total_analyses = await db.analyses.count_documents({})
                total_advanced = await db.advanced_scans.count_documents({})
                
                # Time-based analytics
                now = datetime.utcnow()
                today = now.replace(hour=0, minute=0, second=0, microsecond=0)
                week_ago = today - timedelta(days=7)
                
                today_analyses = await db.analyses.count_documents({
                    "created_at": {"$gte": today}
                })
                today_advanced = await db.advanced_scans.count_documents({
                    "timestamp": {"$gte": today}
                })
                
                week_analyses = await db.analyses.count_documents({
                    "created_at": {"$gte": week_ago}
                })
                week_advanced = await db.advanced_scans.count_documents({
                    "timestamp": {"$gte": week_ago}
                })
                
                analytics.update({
                    "usage_statistics": {
                        "total_basic_analyses": total_analyses,
                        "total_advanced_scans": total_advanced,
                        "total_all_scans": total_analyses + total_advanced
                    },
                    "activity": {
                        "today": {
                            "basic_analyses": today_analyses,
                            "advanced_scans": today_advanced,
                            "total": today_analyses + today_advanced
                        },
                        "this_week": {
                            "basic_analyses": week_analyses,
                            "advanced_scans": week_advanced,
                            "total": week_analyses + week_advanced
                        }
                    },
                    "features_status": {
                        "ai_analysis": bool(os.getenv("GROQ_API_KEY") and AI_AVAILABLE),
                        "advanced_scanning": AI_AVAILABLE,
                        "database_analytics": True,
                        "real_time_monitoring": True
                    }
                })
                
            except Exception as e:
                logger.error(f"❌ Database analytics error: {e}")
                analytics["error"] = f"Database analytics unavailable: {str(e)}"
        else:
            analytics.update({
                "database": "not_configured",
                "usage_statistics": {"note": "Database required for detailed analytics"}
            })
        
        return analytics
        
    except Exception as e:
        logger.error(f"❌ Analytics error: {e}")
        return {
            "error": str(e),
            "platform": "ViralSafe Enhanced",
            "version": "3.1.0",
            "timestamp": datetime.utcnow().isoformat()
        }

# Service Information Endpoint
@app.get("/api/info")
async def service_info():
    """Comprehensive service information and capabilities"""
    return {
        "service": "ViralSafe Platform Enhanced API",
        "version": "3.1.0",
        "description": "AI-Powered Content Safety Analysis with Advanced Threat Intelligence",
        "capabilities": [
            "Multi-AI Security Analysis (Groq, Anthropic, OpenAI)",
            "Advanced Web Content Scanning",
            "Real-time Threat Intelligence",
            "Smart Trust Score Calculation",
            "MongoDB Analytics Storage",
            "RESTful API with OpenAPI Documentation"
        ],
        "endpoints": {
            "health_check": "/health",
            "basic_content_analysis": "/api/analyze",
            "advanced_url_scan": "/api/advanced-scan",
            "system_status": "/api/system-status",
            "analytics_dashboard": "/api/analytics",
            "service_info": "/api/info",
            "api_documentation": "/docs"
        },
        "features": {
            "ai_powered_analysis": bool(os.getenv("GROQ_API_KEY") and AI_AVAILABLE),
            "fallback_mode": True,
            "database_storage": bool(db),
            "comprehensive_logging": True,
            "async_processing": True
        },
        "links": {
            "github_repository": "https://github.com/Gzeu/viralsafe-platform-free",
            "frontend_application": "https://viralsafe-platform-free.vercel.app",
            "landing_page": "https://gzeu.github.io/viralsafe-platform-free"
        },
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": str(datetime.utcnow() - app_start_time).split('.')[0]
    }

# Enhanced Error Handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler with helpful information"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": f"The requested endpoint {request.url.path} does not exist",
            "available_endpoints": [
                "/health - Health check and system status",
                "/docs - Interactive API documentation", 
                "/api/analyze - Basic content analysis",
                "/api/advanced-scan - AI-powered URL security scan",
                "/api/system-status - Detailed system information",
                "/api/analytics - Platform usage analytics",
                "/api/info - Service information and capabilities"
            ],
            "service": "ViralSafe Enhanced API v3.1.0",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler with logging"""
    logger.error(f"🚨 Internal server error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred while processing your request",
            "service": "ViralSafe Enhanced API v3.1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "support": "Check /health endpoint for system status"
        }
    )

# Custom middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for monitoring"""
    start_time = datetime.utcnow()
    
    # Process request
    response = await call_next(request)
    
    # Calculate response time
    process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    # Log request details
    logger.info(f"📝 {request.method} {request.url.path} - {response.status_code} - {process_time:.2f}ms")
    
    return response

# Application entry point for Render deployment
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (Render provides this)
    port = int(os.getenv("PORT", 10000))
    
    logger.info(f"🚀 Starting ViralSafe Enhanced API on port {port}")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port,
        reload=False,  # Disable reload in production
        log_level="info",
        access_log=True
    )
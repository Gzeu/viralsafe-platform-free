from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import os
import json
import hashlib
import time
import logging
import asyncio
from typing import List, Optional, Dict
from datetime import datetime
from contextlib import asynccontextmanager

# Import our modules
from config import settings
from database import db_manager
from virustotal import vt_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In-memory fallback storage
analysis_store: Dict[str, dict] = {}
analytics_fallback = {
    "total_analyses": 0,
    "risk_distribution": {"high": 0, "medium": 0, "low": 0},
    "platform_stats": {},
    "daily_usage": []
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info(f"🛡️ Starting ViralSafe Platform v{settings.API_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Port: {settings.PORT}")
    
    # Initialize database
    if settings.database_configured:
        db_connected = await db_manager.connect()
        if db_connected:
            logger.info("✅ MongoDB Atlas connected successfully")
        else:
            logger.warning("⚠️ MongoDB connection failed, using in-memory storage")
    else:
        logger.warning("⚠️ MongoDB not configured, using in-memory storage")
    
    # Initialize VirusTotal API
    if settings.virustotal_configured:
        vt_initialized = await vt_api.initialize()
        if vt_initialized:
            logger.info("✅ VirusTotal API initialized successfully")
        else:
            logger.warning("⚠️ VirusTotal API initialization failed")
    else:
        logger.warning("⚠️ VirusTotal API not configured")
    
    logger.info("🚀 ViralSafe Platform started successfully!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down ViralSafe Platform...")
    await db_manager.disconnect()
    await vt_api.close()
    logger.info("✅ Shutdown complete")

app = FastAPI(
    title=settings.API_TITLE,
    description="Open Source Content Safety Analysis Platform with MongoDB Atlas & VirusTotal Integration",
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if settings.is_production else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Pydantic Models
class ContentRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=settings.MAX_CONTENT_LENGTH, description="Content to analyze")
    url: Optional[str] = Field(None, description="Source URL if available")
    platform: str = Field("general", description="Platform type (twitter, facebook, telegram, etc)")
    user_agent: Optional[str] = None
    check_urls: bool = Field(True, description="Enable URL scanning with VirusTotal")

class AnalysisResponse(BaseModel):
    id: str
    content_hash: str
    content_preview: str
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str
    categories: List[str]
    indicators: List[str]
    recommendations: List[str]
    platform: str
    timestamp: datetime
    processing_time_ms: int
    virustotal_report: Optional[Dict] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    environment: str
    services: Dict[str, Dict]
    uptime_info: Dict

class AnalyticsResponse(BaseModel):
    total_analyses: int
    risk_distribution: Dict[str, int]
    platform_stats: Dict[str, int]
    avg_risk_score: float
    database_status: str

# Enhanced content analysis with VirusTotal integration
async def analyze_content_safety(content: str, platform: str, url: Optional[str] = None, check_urls: bool = True) -> Dict:
    start_time = time.time()
    
    # Risk indicators database (enhanced)
    high_risk_patterns = [
        "scam", "fake news", "phishing", "malware", "virus", "hack", "steal",
        "urgent action required", "click here now", "limited time", "act fast",
        "congratulations you won", "claim your prize", "verify account",
        "suspended account", "confirm identity", "update payment",
        "crypto investment", "guaranteed profit", "double your money",
        "romance scam", "lonely", "love you", "send money"
    ]
    
    medium_risk_patterns = [
        "unverified", "rumor", "allegedly", "claims", "reports suggest",
        "breaking", "exclusive", "leaked", "insider", "anonymous source",
        "investment opportunity", "quick money", "work from home",
        "weight loss miracle", "medical breakthrough"
    ]
    
    misinformation_indicators = [
        "doctors hate this", "miracle cure", "government hiding",
        "they don't want you to know", "secret revealed", "conspiracy",
        "mainstream media lies", "censored truth", "wake up people"
    ]
    
    # Analysis logic
    content_lower = content.lower()
    risk_score = 0.0
    categories = []
    indicators = []
    virustotal_report = None
    
    # Check high risk patterns
    high_risk_matches = [pattern for pattern in high_risk_patterns if pattern in content_lower]
    if high_risk_matches:
        risk_score += len(high_risk_matches) * 0.25
        categories.append("potential_scam")
        indicators.extend(high_risk_matches[:3])
    
    # Check medium risk patterns
    medium_risk_matches = [pattern for pattern in medium_risk_patterns if pattern in content_lower]
    if medium_risk_matches:
        risk_score += len(medium_risk_matches) * 0.15
        categories.append("unverified_claims")
        indicators.extend(medium_risk_matches[:2])
    
    # Check misinformation
    misinfo_matches = [pattern for pattern in misinformation_indicators if pattern in content_lower]
    if misinfo_matches:
        risk_score += len(misinfo_matches) * 0.2
        categories.append("potential_misinformation")
        indicators.extend(misinfo_matches[:2])
    
    # URL Analysis with VirusTotal
    if check_urls and url and settings.virustotal_configured:
        try:
            vt_report = await vt_api.get_url_report(url)
            if vt_report:
                virustotal_report = vt_report
                vt_risk = vt_report.get('risk_score', 0)
                if vt_risk > 0.7:
                    risk_score += 0.4
                    categories.append("malicious_url")
                    indicators.append(f"virustotal_malicious_detections: {vt_report.get('malicious', 0)}")
                elif vt_risk > 0.3:
                    risk_score += 0.2
                    categories.append("suspicious_url")
                    indicators.append(f"virustotal_suspicious_detections: {vt_report.get('suspicious', 0)}")
        except Exception as e:
            logger.warning(f"VirusTotal URL check failed: {e}")
    
    # Platform-specific risk adjustments
    platform_multipliers = {
        "telegram": 1.2,
        "whatsapp": 1.1,
        "facebook": 1.0,
        "twitter": 0.9,
        "linkedin": 0.8,
        "instagram": 1.0
    }
    
    multiplier = platform_multipliers.get(platform, 1.0)
    risk_score *= multiplier
    
    # Suspicious domain/URL patterns in content
    suspicious_domains = [".tk", ".ml", ".ga", "bit.ly", "tinyurl", "t.co", "shortened"]
    url_matches = [domain for domain in suspicious_domains if domain in content_lower]
    if url_matches:
        risk_score += 0.15
        categories.append("suspicious_links")
        indicators.append("suspicious_url_shorteners_detected")
    
    # Normalize risk score
    risk_score = min(risk_score, 1.0)
    
    # Determine risk level
    if risk_score >= 0.7:
        risk_level = "high"
    elif risk_score >= 0.4:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    # Generate recommendations
    recommendations = []
    if risk_score >= 0.7:
        recommendations = [
            "🚨 HIGH RISK: Do not interact with this content",
            "❌ Do not click any links or provide personal information",
            "📢 Consider reporting this content to the platform",
            "🛡️ Verify information through official sources",
            "⚠️ This content shows multiple risk indicators"
        ]
    elif risk_score >= 0.4:
        recommendations = [
            "⚠️ MEDIUM RISK: Exercise caution",
            "🔍 Verify information from multiple reliable sources",
            "🤔 Be skeptical of sensational claims",
            "📱 Check official accounts/websites for confirmation",
            "🧠 Apply critical thinking before sharing"
        ]
    else:
        recommendations = [
            "✅ LOW RISK: Content appears relatively safe",
            "📚 Still recommended to verify important information",
            "🧠 Use critical thinking when consuming content",
            "👍 Safe to engage with normal caution"
        ]
    
    processing_time = int((time.time() - start_time) * 1000)
    
    return {
        "risk_score": round(risk_score, 3),
        "risk_level": risk_level,
        "categories": categories or ["general"],
        "indicators": indicators or ["no_specific_indicators"],
        "recommendations": recommendations,
        "processing_time_ms": processing_time,
        "virustotal_report": virustotal_report
    }

@app.get("/", response_class=JSONResponse)
async def root():
    config_status = settings.validate_configuration()
    return {
        "message": "🛡️ ViralSafe API - Content Safety Analysis Platform",
        "version": settings.API_VERSION,
        "status": "active",
        "environment": settings.ENVIRONMENT,
        "hosting": "render.com",
        "configuration": {
            "mongodb": "✅ Connected" if config_status["mongodb"] else "❌ Not configured",
            "virustotal": "✅ Connected" if config_status["virustotal"] else "❌ Not configured"
        },
        "endpoints": {
            "health": "/health - System health check",
            "analyze": "/analyze - Content safety analysis",
            "analytics": "/analytics - Usage analytics",
            "docs": "/docs - API documentation"
        },
        "features": [
            "🔍 AI-powered content analysis",
            "🛡️ VirusTotal URL scanning",
            "💾 MongoDB Atlas storage",
            "📊 Real-time analytics",
            "🌐 Multi-platform support"
        ]
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    # Get database health
    db_health = {"status": "not_configured"}
    if settings.database_configured:
        db_health = await db_manager.health_check()
    
    # Get VirusTotal health
    vt_health = {"status": "not_configured"}
    if settings.virustotal_configured:
        vt_health = await vt_api.health_check()
    
    # Overall system status
    overall_status = "healthy"
    if db_health.get("status") == "error" or vt_health.get("status") == "error":
        overall_status = "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version=settings.API_VERSION,
        environment=settings.ENVIRONMENT,
        services={
            "database": db_health,
            "virustotal": vt_health
        },
        uptime_info={
            "analyses_processed": len(analysis_store),
            "memory_usage": len(analysis_store),
            "port": settings.PORT
        }
    )

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: ContentRequest, background_tasks: BackgroundTasks):
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    
    # Generate unique ID
    content_hash = hashlib.sha256(
        (request.content + request.platform + str(time.time())).encode()
    ).hexdigest()[:16]
    analysis_id = f"vs_{int(time.time())}_{content_hash}"
    
    # Run enhanced analysis
    analysis_result = await analyze_content_safety(
        request.content, 
        request.platform, 
        request.url,
        request.check_urls
    )
    
    # Create response
    response = AnalysisResponse(
        id=analysis_id,
        content_hash=content_hash[:12],
        content_preview=request.content[:150] + "..." if len(request.content) > 150 else request.content,
        risk_score=analysis_result["risk_score"],
        risk_level=analysis_result["risk_level"],
        categories=analysis_result["categories"],
        indicators=analysis_result["indicators"],
        recommendations=analysis_result["recommendations"],
        platform=request.platform,
        timestamp=datetime.utcnow(),
        processing_time_ms=analysis_result["processing_time_ms"],
        virustotal_report=analysis_result.get("virustotal_report")
    )
    
    # Store analysis
    analysis_data = response.dict()
    analysis_store[analysis_id] = analysis_data
    
    # Try to store in database
    if db_manager.connected:
        background_tasks.add_task(db_manager.store_analysis, analysis_data)
    
    # Update analytics
    background_tasks.add_task(update_analytics, analysis_result["risk_level"], request.platform)
    
    return response

@app.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    # Try database first
    if db_manager.connected:
        try:
            db_analytics = await db_manager.get_analytics()
            return AnalyticsResponse(
                total_analyses=db_analytics.get("total_analyses", 0),
                risk_distribution=db_analytics.get("risk_distribution", {"high": 0, "medium": 0, "low": 0}),
                platform_stats=analytics_fallback.get("platform_stats", {}),
                avg_risk_score=db_analytics.get("avg_risk_score", 0.0),
                database_status="connected"
            )
        except Exception as e:
            logger.warning(f"Database analytics failed: {e}")
    
    # Fallback to in-memory
    total = len(analysis_store)
    avg_score = 0.0
    
    if total > 0:
        scores = [analysis["risk_score"] for analysis in analysis_store.values()]
        avg_score = sum(scores) / len(scores)
    
    return AnalyticsResponse(
        total_analyses=total,
        risk_distribution=analytics_fallback["risk_distribution"],
        platform_stats=analytics_fallback.get("platform_stats", {}),
        avg_risk_score=round(avg_score, 3),
        database_status="fallback"
    )

@app.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    # Try database first
    if db_manager.connected:
        result = await db_manager.get_analysis(analysis_id)
        if result:
            return result
    
    # Fallback to in-memory
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_store[analysis_id]

def update_analytics(risk_level: str, platform: str):
    """Update analytics data in background"""
    analytics_fallback["total_analyses"] += 1
    analytics_fallback["risk_distribution"][risk_level] += 1
    
    if platform in analytics_fallback["platform_stats"]:
        analytics_fallback["platform_stats"][platform] += 1
    else:
        analytics_fallback["platform_stats"][platform] = 1

# Production server setup
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
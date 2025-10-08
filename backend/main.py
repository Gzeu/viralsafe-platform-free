from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import json
import hashlib
import time
from typing import List, Optional, Dict
from datetime import datetime
import httpx

app = FastAPI(
    title="ViralSafe API",
    description="Open Source Content Safety Analysis Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS pentru free tier (acceptă toate originile)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # În producție specifică domeniile
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage pentru demo (FREE - fără DB cost)
analysis_store: Dict[str, dict] = {}
analytics_data = {
    "total_analyses": 0,
    "risk_distribution": {"high": 0, "medium": 0, "low": 0},
    "platform_stats": {},
    "daily_usage": []
}

class ContentRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="Content to analyze")
    url: Optional[str] = Field(None, description="Source URL if available")
    platform: str = Field("general", description="Platform type (twitter, facebook, telegram, etc)")
    user_agent: Optional[str] = None

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

class AnalyticsResponse(BaseModel):
    total_analyses: int
    risk_distribution: Dict[str, int]
    platform_stats: Dict[str, int]
    avg_risk_score: float

# AI-like analysis logic (FREE - fără API externe)
def analyze_content_safety(content: str, platform: str) -> Dict:
    start_time = time.time()
    
    # Risk indicators database
    high_risk_patterns = [
        "scam", "fake news", "phishing", "malware", "virus", "hack", "steal",
        "urgent action required", "click here now", "limited time", "act fast",
        "congratulations you won", "claim your prize", "verify account",
        "suspended account", "confirm identity", "update payment"
    ]
    
    medium_risk_patterns = [
        "unverified", "rumor", "allegedly", "claims", "reports suggest",
        "breaking", "exclusive", "leaked", "insider", "anonymous source"
    ]
    
    misinformation_indicators = [
        "doctors hate this", "miracle cure", "government hiding",
        "they don't want you to know", "secret revealed", "conspiracy"
    ]
    
    # Analysis logic
    content_lower = content.lower()
    risk_score = 0.0
    categories = []
    indicators = []
    
    # Check high risk patterns
    high_risk_matches = [pattern for pattern in high_risk_patterns if pattern in content_lower]
    if high_risk_matches:
        risk_score += len(high_risk_matches) * 0.3
        categories.append("potential_scam")
        indicators.extend(high_risk_matches[:3])  # Limitează la 3
    
    # Check medium risk patterns
    medium_risk_matches = [pattern for pattern in medium_risk_patterns if pattern in content_lower]
    if medium_risk_matches:
        risk_score += len(medium_risk_matches) * 0.15
        categories.append("unverified_claims")
        indicators.extend(medium_risk_matches[:2])
    
    # Check misinformation
    misinfo_matches = [pattern for pattern in misinformation_indicators if pattern in content_lower]
    if misinfo_matches:
        risk_score += len(misinfo_matches) * 0.25
        categories.append("potential_misinformation")
        indicators.extend(misinfo_matches[:2])
    
    # Platform-specific adjustments
    if platform == "telegram":
        risk_score *= 1.1  # Telegram are risc mai mare
    elif platform == "twitter":
        risk_score *= 0.9   # Twitter are moderare mai bună
    
    # URL analysis
    suspicious_domains = [".tk", ".ml", ".ga", "bit.ly", "tinyurl", "shortened"]
    if any(domain in content_lower for domain in suspicious_domains):
        risk_score += 0.2
        categories.append("suspicious_links")
        indicators.append("suspicious_url_detected")
    
    # Normalizează score-ul
    risk_score = min(risk_score, 1.0)
    
    # Determină nivelul de risc
    if risk_score >= 0.7:
        risk_level = "high"
    elif risk_score >= 0.4:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    # Recomandări bazate pe risc
    recommendations = []
    if risk_score >= 0.7:
        recommendations = [
            "🚨 HIGH RISK: Do not interact with this content",
            "❌ Do not click any links or provide personal information",
            "📢 Consider reporting this content to the platform",
            "🛡️ Verify information through official sources"
        ]
    elif risk_score >= 0.4:
        recommendations = [
            "⚠️ MEDIUM RISK: Exercise caution",
            "🔍 Verify information from multiple reliable sources",
            "🤔 Be skeptical of sensational claims",
            "📱 Check official accounts/websites for confirmation"
        ]
    else:
        recommendations = [
            "✅ LOW RISK: Content appears relatively safe",
            "📚 Still recommended to verify important information",
            "🧠 Use critical thinking when consuming content"
        ]
    
    processing_time = int((time.time() - start_time) * 1000)
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "categories": categories or ["general"],
        "indicators": indicators or ["no_specific_indicators"],
        "recommendations": recommendations,
        "processing_time_ms": processing_time
    }

@app.get("/")
def root():
    return {
        "message": "🛡️ ViralSafe API - Content Safety Analysis",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "analytics": "/analytics",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "analyses_in_memory": len(analysis_store),
        "uptime": "ok"
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: ContentRequest, background_tasks: BackgroundTasks):
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    
    # Generate unique ID pentru analysis
    content_hash = hashlib.md5(request.content.encode()).hexdigest()[:12]
    analysis_id = f"vs_{int(time.time())}_{content_hash}"
    
    # Run analysis
    analysis_result = analyze_content_safety(request.content, request.platform)
    
    # Create response
    response = AnalysisResponse(
        id=analysis_id,
        content_hash=content_hash,
        content_preview=request.content[:150] + "..." if len(request.content) > 150 else request.content,
        risk_score=analysis_result["risk_score"],
        risk_level=analysis_result["risk_level"],
        categories=analysis_result["categories"],
        indicators=analysis_result["indicators"],
        recommendations=analysis_result["recommendations"],
        platform=request.platform,
        timestamp=datetime.now(),
        processing_time_ms=analysis_result["processing_time_ms"]
    )
    
    # Store pentru analytics
    analysis_store[analysis_id] = response.dict()
    
    # Update analytics în background
    background_tasks.add_task(update_analytics, analysis_result["risk_level"], request.platform)
    
    return response

@app.get("/analytics", response_model=AnalyticsResponse)
def get_analytics():
    total = len(analysis_store)
    avg_score = 0.0
    
    if total > 0:
        scores = [analysis["risk_score"] for analysis in analysis_store.values()]
        avg_score = sum(scores) / len(scores)
    
    return AnalyticsResponse(
        total_analyses=total,
        risk_distribution=analytics_data["risk_distribution"],
        platform_stats=analytics_data["platform_stats"],
        avg_risk_score=round(avg_score, 3)
    )

@app.get("/analysis/{analysis_id}")
def get_analysis(analysis_id: str):
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis_store[analysis_id]

def update_analytics(risk_level: str, platform: str):
    """Update analytics data in background"""
    analytics_data["total_analyses"] += 1
    analytics_data["risk_distribution"][risk_level] += 1
    
    if platform in analytics_data["platform_stats"]:
        analytics_data["platform_stats"][platform] += 1
    else:
        analytics_data["platform_stats"][platform] = 1

# Pentru deployment pe Railway/Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
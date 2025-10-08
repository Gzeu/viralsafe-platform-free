from fastapi import FastAPI, HTTPException, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import json
import hashlib
import time
from typing import List, Optional, Dict
from datetime import datetime
import httpx
import re
from urllib.parse import urlparse

# Import our new services
from services.verification_apis import verification_apis
from services.badge_generator import badge_generator

app = FastAPI(
    title="ViralSafe API",
    description="Open Source Content Safety Analysis Platform with URL Verification",
    version="1.2.0",
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
url_verification_store: Dict[str, dict] = {}
analytics_data = {
    "total_analyses": 0,
    "risk_distribution": {"high": 0, "medium": 0, "low": 0},
    "platform_stats": {},
    "daily_usage": [],
    "verified_domains": 0,
    "badge_requests": 0
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
    url_verification: Optional[Dict] = None

class URLVerificationRequest(BaseModel):
    url: str = Field(..., description="URL to verify")
    force_refresh: bool = Field(False, description="Force refresh verification")

class URLVerificationResponse(BaseModel):
    url: str
    domain: str
    safety_score: float
    status: str
    risk_level: str
    verified: bool
    sources_checked: int
    source_results: List[Dict]
    timestamp: datetime
    cached: bool = False

class BadgeRequest(BaseModel):
    domain: str
    style: str = Field("modern", description="Badge style: modern, shield, minimal, classic")
    format: str = Field("svg", description="Response format: svg, html, markdown")

class AnalyticsResponse(BaseModel):
    total_analyses: int
    risk_distribution: Dict[str, int]
    platform_stats: Dict[str, int]
    avg_risk_score: float
    verified_domains: int
    badge_requests: int

def extract_urls_from_content(content: str) -> List[str]:
    """Extract URLs from content using regex"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, content)
    return urls

def get_domain_from_url(url: str) -> str:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except:
        return url

# AI-like analysis logic (FREE - fără API externe) - Enhanced version
def analyze_content_safety(content: str, platform: str, extracted_urls: List[str] = None) -> Dict:
    start_time = time.time()
    
    # Enhanced risk indicators database
    high_risk_patterns = [
        "scam", "fake news", "phishing", "malware", "virus", "hack", "steal",
        "urgent action required", "click here now", "limited time", "act fast",
        "congratulations you won", "claim your prize", "verify account",
        "suspended account", "confirm identity", "update payment",
        "free money", "get rich quick", "miracle cure", "lose weight fast"
    ]
    
    medium_risk_patterns = [
        "unverified", "rumor", "allegedly", "claims", "reports suggest",
        "breaking", "exclusive", "leaked", "insider", "anonymous source",
        "amazing opportunity", "limited offer", "act now", "don't miss out"
    ]
    
    misinformation_indicators = [
        "doctors hate this", "government hiding", "they don't want you to know", 
        "secret revealed", "conspiracy", "mainstream media won't tell you",
        "big pharma", "covered up", "suppressed information"
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
        risk_score += len(misinfo_matches) * 0.25
        categories.append("potential_misinformation")
        indicators.extend(misinfo_matches[:2])
    
    # Enhanced URL analysis
    if extracted_urls:
        suspicious_domains = [
            ".tk", ".ml", ".ga", ".cf", "bit.ly", "tinyurl", "shortened",
            "t.co", "goo.gl", "ow.ly", "buff.ly", "short"
        ]
        
        suspicious_keywords = [
            "free", "win", "prize", "gift", "money", "cash", "reward",
            "secure", "verify", "update", "confirm", "click", "urgent"
        ]
        
        for url in extracted_urls:
            # Check for suspicious domains
            if any(domain in url.lower() for domain in suspicious_domains):
                risk_score += 0.2
                categories.append("suspicious_links")
                indicators.append("suspicious_url_detected")
            
            # Check for suspicious keywords in URL
            if any(keyword in url.lower() for keyword in suspicious_keywords):
                risk_score += 0.1
                if "suspicious_links" not in categories:
                    categories.append("suspicious_links")
    
    # Platform-specific adjustments
    platform_multipliers = {
        "telegram": 1.1,
        "whatsapp": 1.05,
        "sms": 1.15,
        "email": 1.1,
        "twitter": 0.95,
        "facebook": 0.9,
        "instagram": 0.9
    }
    
    risk_score *= platform_multipliers.get(platform, 1.0)
    
    # Normalizează score-ul
    risk_score = min(risk_score, 1.0)
    
    # Determină nivelul de risc
    if risk_score >= 0.7:
        risk_level = "high"
    elif risk_score >= 0.4:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    # Enhanced recommendations
    recommendations = []
    if risk_score >= 0.7:
        recommendations = [
            "🚨 HIGH RISK: Do not interact with this content",
            "❌ Do not click any links or provide personal information",
            "📢 Consider reporting this content to the platform",
            "🛡️ Verify information through official sources",
            "⚠️ This appears to be a potential scam or malicious content"
        ]
    elif risk_score >= 0.4:
        recommendations = [
            "⚠️ MEDIUM RISK: Exercise caution",
            "🔍 Verify information from multiple reliable sources",
            "🤔 Be skeptical of sensational claims",
            "📱 Check official accounts/websites for confirmation",
            "🧐 Consider the source and motivation behind this content"
        ]
    else:
        recommendations = [
            "✅ LOW RISK: Content appears relatively safe",
            "📚 Still recommended to verify important information",
            "🧠 Use critical thinking when consuming content",
            "📖 Cross-reference with trusted news sources if needed"
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
        "message": "🛡️ ViralSafe API v1.2 - Enhanced Content Safety & URL Verification",
        "version": "1.2.0",
        "status": "active",
        "hosting": "render.com",
        "new_features": [
            "URL Verification with external APIs",
            "SVG Badge Generation", 
            "Website Verification Status",
            "Enhanced Content Analysis"
        ],
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "verify_url": "/verify/{url}",
            "badge": "/badge/verified/{domain}",
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
        "verified_urls": len(url_verification_store),
        "uptime": "ok",
        "hosting": "render.com",
        "version": "1.2.0"
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: ContentRequest, background_tasks: BackgroundTasks):
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    
    # Extract URLs from content
    extracted_urls = extract_urls_from_content(request.content)
    
    # Generate unique ID pentru analysis
    content_hash = hashlib.md5(request.content.encode()).hexdigest()[:12]
    analysis_id = f"vs_{int(time.time())}_{content_hash}"
    
    # Run enhanced analysis
    analysis_result = analyze_content_safety(request.content, request.platform, extracted_urls)
    
    # URL verification (doar pentru primul URL găsit)
    url_verification = None
    if extracted_urls:
        try:
            first_url = extracted_urls[0]
            domain = get_domain_from_url(first_url)
            
            # Verifică cache
            cache_key = hashlib.md5(first_url.encode()).hexdigest()
            if cache_key in url_verification_store:
                cached_verification = url_verification_store[cache_key]
                # Cache valid pentru 1 oră
                if (datetime.now() - datetime.fromisoformat(cached_verification['timestamp'])).seconds < 3600:
                    url_verification = cached_verification
                    url_verification['cached'] = True
            
            # Dacă nu e în cache, verifică cu API-urile externe
            if not url_verification:
                verification_result = await verification_apis.aggregate_url_verification(first_url)
                url_verification = verification_result
                url_verification['cached'] = False
                url_verification_store[cache_key] = verification_result
                
        except Exception as e:
            url_verification = {"error": f"URL verification failed: {str(e)}"}
    
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
        processing_time_ms=analysis_result["processing_time_ms"],
        url_verification=url_verification
    )
    
    # Store pentru analytics
    analysis_store[analysis_id] = response.dict()
    
    # Update analytics în background
    background_tasks.add_task(update_analytics, analysis_result["risk_level"], request.platform)
    
    return response

@app.post("/verify-url", response_model=URLVerificationResponse)
async def verify_url_endpoint(request: URLVerificationRequest):
    """Verify a URL using multiple external security APIs"""
    
    if not request.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    
    try:
        domain = get_domain_from_url(request.url)
        cache_key = hashlib.md5(request.url.encode()).hexdigest()
        
        # Check cache unless force refresh
        if not request.force_refresh and cache_key in url_verification_store:
            cached_result = url_verification_store[cache_key]
            # Cache valid pentru 1 oră
            if (datetime.now() - datetime.fromisoformat(cached_result['timestamp'])).seconds < 3600:
                cached_result['cached'] = True
                return URLVerificationResponse(**cached_result)
        
        # Run verification with external APIs
        verification_result = await verification_apis.aggregate_url_verification(request.url)
        
        # Cache result
        url_verification_store[cache_key] = verification_result
        verification_result['cached'] = False
        
        # Update analytics
        analytics_data["verified_domains"] += 1
        
        return URLVerificationResponse(
            url=verification_result['url'],
            domain=domain,
            safety_score=verification_result['safety_score'],
            status=verification_result['status'],
            risk_level=verification_result['risk_level'],
            verified=verification_result['verified'],
            sources_checked=verification_result['sources_checked'],
            source_results=verification_result['source_results'],
            timestamp=datetime.fromisoformat(verification_result['timestamp']),
            cached=False
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL verification failed: {str(e)}")

@app.get("/verify/{domain}")
async def verify_domain(domain: str):
    """Get verification status for a domain"""
    
    try:
        # Construiește URL-ul complet
        url = f"https://{domain}"
        verification_result = await verification_apis.aggregate_url_verification(url)
        
        return {
            "domain": domain,
            "verified": verification_result['verified'],
            "safety_score": verification_result['safety_score'],
            "status": verification_result['status'],
            "risk_level": verification_result['risk_level'],
            "sources_checked": verification_result['sources_checked'],
            "last_checked": verification_result['timestamp'],
            "summary": verification_result.get('summary', ''),
            "badge_available": True
        }
        
    except Exception as e:
        return {
            "domain": domain,
            "error": str(e),
            "verified": False,
            "badge_available": False
        }

@app.get("/badge/verified/{domain}")
async def get_verification_badge(domain: str, style: str = "modern"):
    """Generate verification badge for a domain"""
    
    try:
        # Get verification status
        url = f"https://{domain}"
        verification_result = await verification_apis.aggregate_url_verification(url)
        
        safety_score = verification_result.get('safety_score', 0.5)
        verified = verification_result.get('verified', False)
        
        # Generate appropriate badge
        if verified and safety_score >= 0.8:
            badge_svg = badge_generator.generate_verified_badge(domain, safety_score, style)
        else:
            badge_svg = badge_generator.generate_warning_badge(domain, safety_score, style)
        
        # Update analytics
        analytics_data["badge_requests"] += 1
        
        return Response(content=badge_svg, media_type="image/svg+xml")
        
    except Exception as e:
        # Generate error badge
        error_svg = f'''<svg width="140" height="30" xmlns="http://www.w3.org/2000/svg">
            <rect width="140" height="30" rx="5" fill="#fee2e2" stroke="#dc2626" stroke-width="2"/>
            <text x="70" y="20" text-anchor="middle" font-family="Arial,sans-serif" font-size="10" fill="#dc2626">Verification Error</text>
        </svg>'''
        return Response(content=error_svg, media_type="image/svg+xml")

@app.get("/badge/embed/{domain}")
async def get_badge_embed_code(domain: str, style: str = "modern", format: str = "html"):
    """Get embed code for verification badge"""
    
    try:
        embed_code = badge_generator.generate_embed_code(domain, style, format)
        return {
            "domain": domain,
            "style": style,
            "format": format,
            "embed_code": embed_code,
            "preview_url": f"/badge/verified/{domain}?style={style}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embed code: {str(e)}")

@app.get("/widget/{domain}")
async def get_widget_code(domain: str):
    """Get JavaScript widget code for a domain"""
    
    try:
        widget_code = badge_generator.generate_widget_code(domain)
        return {
            "domain": domain,
            "widget_code": widget_code,
            "integration_guide": {
                "step1": "Copy the widget code",
                "step2": "Paste it before the closing </body> tag on your website",
                "step3": "The widget will automatically verify your domain and display status"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate widget: {str(e)}")

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
        avg_risk_score=round(avg_score, 3),
        verified_domains=analytics_data["verified_domains"],
        badge_requests=analytics_data["badge_requests"]
    )

@app.get("/analysis/{analysis_id}")
def get_analysis(analysis_id: str):
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis_store[analysis_id]

@app.get("/badge/styles")
def get_badge_styles():
    """Get available badge styles with previews"""
    base_url = "https://viralsafe-backend.onrender.com"
    
    return {
        "styles": [
            {
                "name": "modern",
                "description": "Modern gradient design with drop shadow",
                "preview": f"{base_url}/badge/verified/example.com?style=modern",
                "recommended": True
            },
            {
                "name": "shield",
                "description": "Shield-shaped security badge",
                "preview": f"{base_url}/badge/verified/example.com?style=shield"
            },
            {
                "name": "minimal",
                "description": "Clean, minimal design",
                "preview": f"{base_url}/badge/verified/example.com?style=minimal"
            },
            {
                "name": "classic",
                "description": "Traditional button style",
                "preview": f"{base_url}/badge/verified/example.com?style=classic"
            }
        ]
    }

def update_analytics(risk_level: str, platform: str):
    """Update analytics data in background"""
    analytics_data["total_analyses"] += 1
    analytics_data["risk_distribution"][risk_level] += 1
    
    if platform in analytics_data["platform_stats"]:
        analytics_data["platform_stats"][platform] += 1
    else:
        analytics_data["platform_stats"][platform] = 1

# Cleanup function pentru cache
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    pass

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await verification_apis.close()

# Pentru deployment pe Render/Railway (port flexibil)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))  # Render folosește 10000, Railway 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
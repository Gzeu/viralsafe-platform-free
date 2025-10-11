import os
import json
import time
import asyncio
import requests
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedAIAnalyzer:
    """
    Enhanced AI Analyzer with multi-provider support and comprehensive fallback
    Supports Groq (primary), Anthropic, OpenAI with graceful degradation
    """
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            logger.warning("⚠️ GROQ_API_KEY not found - AI features will use fallback mode")
            self.groq_client = None
        else:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("✅ Groq AI client initialized successfully")
            except ImportError:
                logger.error("❌ Groq package not installed - run: pip install groq")
                self.groq_client = None
            except Exception as e:
                logger.error(f"❌ Groq initialization failed: {e}")
                self.groq_client = None
        
        self.model = "mixtral-8x7b-32768"
        
    async def analyze_url_advanced(self, url: str) -> Dict[str, Any]:
        """
        Advanced AI-powered URL security analysis with comprehensive fallback
        """
        start_time = time.time()
        
        # Validate URL format
        if not self._is_valid_url(url):
            raise ValueError("Invalid URL format provided")
        
        # Fetch URL content safely
        content_data = await self._safe_fetch_content(url)
        
        # Run AI security analysis
        try:
            if self.groq_client:
                ai_analysis = await self._run_groq_analysis(url, content_data)
                logger.info(f"✅ AI analysis completed for {url}")
            else:
                ai_analysis = self._fallback_analysis()
                logger.info(f"⚠️ Using fallback analysis for {url}")
        except Exception as e:
            logger.error(f"❌ AI analysis failed for {url}: {e}")
            ai_analysis = self._fallback_analysis()
        
        # Calculate composite trust score
        trust_score = self._calculate_trust_score(ai_analysis, content_data)
        scan_time = int((time.time() - start_time) * 1000)
        
        result = {
            "url": url,
            "trust_score": trust_score,
            "threat_level": ai_analysis.get("threat_level", 3),
            "ai_confidence": ai_analysis.get("confidence", 85),
            "ai_insights": ai_analysis.get("insights", "Security analysis completed using advanced algorithms."),
            "recommendations": ai_analysis.get("recommendations", ["Regular monitoring recommended", "Verify SSL certificate status"]),
            "scan_time": scan_time,
            "status_code": content_data.get("status_code", 0),
            "categories": ai_analysis.get("categories", ["Web Content"]),
            "risk_factors": ai_analysis.get("risk_factors", ["Analysis completed successfully"]),
            "ai_provider": "groq" if self.groq_client else "fallback",
            "enhanced_mode": True,
            "version": "3.1.0"
        }
        
        logger.info(f"📊 Scan completed: Trust Score {trust_score}% in {scan_time}ms")
        return result
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    async def _safe_fetch_content(self, url: str) -> Dict[str, Any]:
        """Safely fetch URL content with comprehensive error handling"""
        try:
            headers = {
                'User-Agent': 'ViralSafe-Enhanced-Scanner/3.1 (Security-Analysis)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache'
            }
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: requests.get(url, headers=headers, timeout=8, allow_redirects=True, verify=True)
            )
            
            return {
                "status_code": response.status_code,
                "content": response.text[:2000],  # First 2KB for analysis
                "headers": dict(response.headers),
                "final_url": response.url,
                "redirected": response.url != url,
                "content_length": len(response.text),
                "encoding": response.encoding or 'utf-8'
            }
            
        except requests.exceptions.Timeout:
            logger.warning(f"⏰ Request timeout for {url}")
            return {"status_code": 408, "content": "", "error": "Request timeout", "timeout": True}
        except requests.exceptions.SSLError as e:
            logger.warning(f"🔒 SSL error for {url}: {e}")
            return {"status_code": 495, "content": "", "error": "SSL certificate error", "ssl_error": True}
        except requests.exceptions.ConnectionError:
            logger.warning(f"🌐 Connection error for {url}")
            return {"status_code": 0, "content": "", "error": "Connection failed", "connection_error": True}
        except Exception as e:
            logger.error(f"❌ Fetch error for {url}: {e}")
            return {"status_code": 0, "content": "", "error": str(e)}
    
    async def _run_groq_analysis(self, url: str, content_data: Dict) -> Dict[str, Any]:
        """Run AI analysis using Groq API with enhanced prompting"""
        
        domain = urlparse(url).netloc
        content = content_data.get("content", "")
        status_code = content_data.get("status_code", 0)
        
        # Enhanced security analysis prompt
        prompt = f"""Analyze this website for security threats and provide a professional assessment.

URL: {url}
Domain: {domain}
HTTP Status: {status_code}
Content Sample: {content[:1000]}

Analyze for: malware indicators, phishing patterns, suspicious content, domain reputation, SSL security.

Respond with ONLY valid JSON:
{{
  "threat_level": 1-10,
  "confidence": 75-99,
  "insights": "Professional security assessment (max 120 characters)",
  "recommendations": ["actionable recommendation 1", "actionable recommendation 2"],
  "categories": ["primary category", "secondary category"],
  "risk_factors": ["specific risk factor 1", "specific risk factor 2"]
}}

Be accurate and professional. Use lower threat_level (1-3) for legitimate sites."""

        try:
            # Make API call to Groq
            response = await self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional cybersecurity analyst. Always respond with valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=500
            )
            
            # Extract and clean response
            content = response.choices.message.content.strip()
            
            # Remove any markdown formatting
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            # Parse JSON response
            result = json.loads(content)
            
            # Validate and sanitize result
            result = self._validate_ai_response(result)
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error in Groq response: {e}")
            raise Exception("Failed to parse AI analysis response")
        except Exception as e:
            logger.error(f"❌ Groq API error: {e}")
            raise Exception(f"AI analysis service error: {str(e)}")
    
    def _validate_ai_response(self, result: Dict) -> Dict:
        """Validate and sanitize AI response"""
        # Ensure required fields exist
        required_fields = ["threat_level", "confidence", "insights", "recommendations", "categories", "risk_factors"]
        for field in required_fields:
            if field not in result:
                result[field] = self._get_default_value(field)
        
        # Validate data types and ranges
        if not isinstance(result["threat_level"], int) or not 1 <= result["threat_level"] <= 10:
            result["threat_level"] = 5
        
        if not isinstance(result["confidence"], int) or not 75 <= result["confidence"] <= 99:
            result["confidence"] = 85
        
        # Ensure string fields are strings
        if not isinstance(result["insights"], str):
            result["insights"] = "Security analysis completed successfully."
        
        # Ensure list fields are lists
        for field in ["recommendations", "categories", "risk_factors"]:
            if not isinstance(result[field], list):
                result[field] = [str(result[field])] if result[field] else ["Not specified"]
        
        return result
    
    def _get_default_value(self, field: str):
        """Get default values for missing fields"""
        defaults = {
            "threat_level": 5,
            "confidence": 85,
            "insights": "Security analysis completed successfully.",
            "recommendations": ["Regular monitoring recommended"],
            "categories": ["Web Content"],
            "risk_factors": ["Standard web content"]
        }
        return defaults.get(field, "Unknown")
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """Enhanced fallback analysis when AI is unavailable"""
        return {
            "threat_level": 4,
            "confidence": 80,
            "insights": "Fallback security analysis completed. Enhanced AI features require API configuration.",
            "recommendations": [
                "Verify SSL certificate and security headers manually",
                "Check domain reputation with additional security tools",
                "Enable AI features for comprehensive analysis"
            ],
            "categories": ["Web Content", "Requires Enhanced Analysis"],
            "risk_factors": [
                "AI analysis service temporarily unavailable",
                "Manual verification recommended for critical applications"
            ]
        }
    
    def _calculate_trust_score(self, ai_analysis: Dict, content_data: Dict) -> int:
        """Calculate composite trust score from multiple factors"""
        base_score = 85  # Start with neutral-positive baseline
        
        # AI threat level impact (primary factor)
        threat_level = ai_analysis.get("threat_level", 5)
        threat_penalty = (threat_level - 1) * 8
        base_score -= threat_penalty
        
        # HTTP status code impact
        status_code = content_data.get("status_code", 0)
        if status_code == 200:
            base_score += 5  # Bonus for successful response
        elif status_code in [301, 302, 303, 307, 308]:
            base_score -= 2  # Minor penalty for redirects
        elif status_code in [400, 401, 403, 404]:
            base_score -= 8  # Moderate penalty for client errors
        elif status_code in [500, 501, 502, 503, 504]:
            base_score -= 12  # Server error penalty
        elif status_code == 0:
            base_score -= 15  # Major penalty for connection issues
        else:
            base_score -= 10  # General penalty for other errors
        
        # Security-specific penalties
        if content_data.get("ssl_error"):
            base_score -= 20  # Major penalty for SSL issues
        elif content_data.get("timeout"):
            base_score -= 5   # Minor penalty for slow response
        elif content_data.get("connection_error"):
            base_score -= 15  # Moderate penalty for connection issues
        
        # AI confidence impact
        confidence = ai_analysis.get("confidence", 85)
        if confidence >= 95:
            base_score += 3   # Bonus for high confidence
        elif confidence >= 90:
            base_score += 1   # Small bonus
        elif confidence < 80:
            base_score -= 5   # Penalty for low confidence
        
        # Content quality indicators
        if content_data.get("content"):
            content_length = len(content_data.get("content", ""))
            if content_length > 500:
                base_score += 2  # Bonus for substantial content
            elif content_length < 100:
                base_score -= 3  # Penalty for minimal content
        
        # HTTPS bonus
        if content_data.get("final_url", "").startswith("https://"):
            base_score += 3  # Bonus for HTTPS
        
        # Ensure score stays within valid bounds
        final_score = max(0, min(100, base_score))
        
        return final_score

# Test function for development
async def test_analyzer():
    """Test function for development purposes"""
    try:
        analyzer = AdvancedAIAnalyzer()
        test_urls = ["https://google.com", "https://github.com"]
        
        for url in test_urls:
            logger.info(f"🧪 Testing analysis for {url}")
            result = await analyzer.analyze_url_advanced(url)
            print(f"✅ Results for {url}:")
            print(json.dumps(result, indent=2))
            print("-" * 50)
        
        return True
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_analyzer())
import asyncio
import logging
import hashlib
import time
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import httpx
from config import settings

logger = logging.getLogger(__name__)

class VirusTotalAPI:
    """VirusTotal API integration with improved error handling and stable endpoints"""
    
    def __init__(self):
        self.base_url = settings.VIRUSTOTAL_BASE_URL
        self.api_key = settings.VIRUSTOTAL_API_KEY
        self.rate_limit = settings.VIRUSTOTAL_RATE_LIMIT
        self.request_times = []  # Track request timestamps for rate limiting
        self.client: Optional[httpx.AsyncClient] = None
        self.is_healthy = False
        
        # Stable test endpoints that work reliably with free API
        self.test_endpoints = [
            "/domains/google.com",
            "/ip_addresses/8.8.8.8",
            "/domains/github.com"
        ]
    
    async def initialize(self) -> bool:
        """Initialize HTTP client and validate API key with stable endpoints"""
        try:
            if not self.api_key:
                logger.warning("⚠️ VirusTotal API key not configured - running in degraded mode")
                self.is_healthy = False
                return False
            
            self.client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "x-apikey": self.api_key,
                    "User-Agent": "ViralSafe/1.0"
                }
            )
            
            # Test API connection with stable endpoints instead of /users/self
            connection_success = await self._test_connection()
            
            if connection_success:
                logger.info("✅ VirusTotal API initialized successfully")
                self.is_healthy = True
                return True
            else:
                logger.warning("⚠️ VirusTotal API connection failed - running in degraded mode")
                self.is_healthy = False
                return False
                
        except Exception as e:
            logger.error(f"❌ VirusTotal API initialization failed: {e}")
            self.is_healthy = False
            return False
    
    async def _test_connection(self) -> bool:
        """Test connection using stable endpoints that work with free tier"""
        for endpoint in self.test_endpoints:
            try:
                logger.info(f"🔍 Testing VirusTotal endpoint: {endpoint}")
                response = await self.client.get(
                    f"{self.base_url}{endpoint}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ VirusTotal API test successful with {endpoint}")
                    return True
                elif response.status_code == 401:
                    logger.error("❌ VirusTotal API: Invalid API key")
                    return False
                elif response.status_code == 403:
                    logger.error("❌ VirusTotal API: Access forbidden - check API key permissions")
                    return False
                else:
                    logger.warning(f"⚠️ VirusTotal endpoint {endpoint}: HTTP {response.status_code}")
                    continue
                    
            except asyncio.TimeoutError:
                logger.warning(f"⏰ VirusTotal endpoint {endpoint}: Timeout")
                continue
            except Exception as e:
                logger.warning(f"⚠️ VirusTotal endpoint {endpoint}: {e}")
                continue
        
        logger.error("❌ All VirusTotal test endpoints failed")
        return False
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
    
    async def _rate_limit_check(self):
        """Check and enforce rate limiting (4 requests per minute for free tier)"""
        now = time.time()
        
        # Remove requests older than 1 minute
        self.request_times = [req_time for req_time in self.request_times if now - req_time < 60]
        
        # Check if we can make another request
        if len(self.request_times) >= self.rate_limit:
            # Calculate wait time
            oldest_request = min(self.request_times)
            wait_time = 60 - (now - oldest_request) + 1  # +1 second buffer
            
            if wait_time > 0:
                logger.info(f"⏰ Rate limit reached, waiting {wait_time:.1f} seconds")
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.request_times.append(now)
    
    async def scan_url(self, url: str) -> Optional[Dict]:
        """Submit URL for scanning with fallback handling"""
        try:
            if not self.is_healthy or not self.client:
                logger.warning("⚠️ VirusTotal unavailable - skipping URL scan")
                return self._create_fallback_response("url_scan", {"url": url})
            
            await self._rate_limit_check()
            
            # Submit URL for scanning
            scan_data = {"url": url}
            response = await self.client.post(
                f"{self.base_url}/urls", 
                data=scan_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                scan_id = result.get("data", {}).get("id")
                
                logger.info(f"✅ URL scan submitted: {scan_id}")
                return {
                    "scan_id": scan_id, 
                    "url": url, 
                    "submitted_at": datetime.utcnow().isoformat(),
                    "status": "submitted"
                }
            else:
                logger.error(f"❌ URL scan failed: HTTP {response.status_code}")
                return self._create_fallback_response("url_scan", {"url": url, "error": f"HTTP {response.status_code}"})
                
        except asyncio.TimeoutError:
            logger.error(f"⏰ URL scan timeout for: {url}")
            return self._create_fallback_response("url_scan", {"url": url, "error": "timeout"})
        except Exception as e:
            logger.error(f"❌ URL scan error: {e}")
            return self._create_fallback_response("url_scan", {"url": url, "error": str(e)})
    
    async def get_url_report(self, url: str) -> Optional[Dict]:
        """Get URL analysis report with fallback handling"""
        try:
            if not self.is_healthy or not self.client:
                logger.warning("⚠️ VirusTotal unavailable - using fallback analysis")
                return self._create_fallback_response("url_report", {"url": url})
            
            await self._rate_limit_check()
            
            # Create URL ID for lookup
            url_id = self._get_url_id(url)
            
            response = await self.client.get(
                f"{self.base_url}/urls/{url_id}",
                timeout=30.0
            )
            
            if response.status_code == 200:
                return self._parse_url_report(response.json())
            elif response.status_code == 404:
                # URL not found, submit for scanning
                logger.info(f"🔍 URL not found in VT database, submitting for scan: {url}")
                await self.scan_url(url)
                return self._create_fallback_response("url_report", {"url": url, "status": "not_found"})
            else:
                logger.error(f"❌ URL report failed: HTTP {response.status_code}")
                return self._create_fallback_response("url_report", {"url": url, "error": f"HTTP {response.status_code}"})
                
        except asyncio.TimeoutError:
            logger.error(f"⏰ URL report timeout for: {url}")
            return self._create_fallback_response("url_report", {"url": url, "error": "timeout"})
        except Exception as e:
            logger.error(f"❌ URL report error: {e}")
            return self._create_fallback_response("url_report", {"url": url, "error": str(e)})
    
    async def scan_file_hash(self, file_hash: str) -> Optional[Dict]:
        """Get file hash analysis report with fallback handling"""
        try:
            if not self.is_healthy or not self.client:
                logger.warning("⚠️ VirusTotal unavailable - using fallback analysis")
                return self._create_fallback_response("file_hash", {"hash": file_hash})
            
            await self._rate_limit_check()
            
            response = await self.client.get(
                f"{self.base_url}/files/{file_hash}",
                timeout=30.0
            )
            
            if response.status_code == 200:
                return self._parse_file_report(response.json())
            elif response.status_code == 404:
                logger.info(f"🔍 File hash not found in VT database: {file_hash}")
                return self._create_fallback_response("file_hash", {"hash": file_hash, "status": "not_found"})
            else:
                logger.error(f"❌ File hash report failed: HTTP {response.status_code}")
                return self._create_fallback_response("file_hash", {"hash": file_hash, "error": f"HTTP {response.status_code}"})
                
        except asyncio.TimeoutError:
            logger.error(f"⏰ File hash timeout for: {file_hash}")
            return self._create_fallback_response("file_hash", {"hash": file_hash, "error": "timeout"})
        except Exception as e:
            logger.error(f"❌ File hash error: {e}")
            return self._create_fallback_response("file_hash", {"hash": file_hash, "error": str(e)})
    
    def _create_fallback_response(self, scan_type: str, metadata: Dict) -> Dict:
        """Create fallback response when VirusTotal is unavailable"""
        return {
            "fallback": True,
            "scan_type": scan_type,
            "status": "degraded",
            "message": "VirusTotal API unavailable - using basic analysis",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata,
            "risk_score": 0.0,
            "confidence": "low"
        }
    
    def _get_url_id(self, url: str) -> str:
        """Generate VirusTotal URL ID"""
        return hashlib.sha256(url.encode()).hexdigest()
    
    def _parse_url_report(self, data: dict) -> Dict:
        """Parse VirusTotal URL report"""
        try:
            attributes = data.get("data", {}).get("attributes", {})
            stats = attributes.get("last_analysis_stats", {})
            
            total_engines = sum(stats.values())
            malicious_count = stats.get("malicious", 0)
            suspicious_count = stats.get("suspicious", 0)
            
            risk_score = 0.0
            if total_engines > 0:
                risk_score = (malicious_count + suspicious_count * 0.5) / total_engines
            
            # Get scan date
            scan_date = attributes.get("last_analysis_date")
            scan_datetime = datetime.fromtimestamp(scan_date) if scan_date else None
            
            return {
                "url": attributes.get("url"),
                "risk_score": round(risk_score, 3),
                "total_engines": total_engines,
                "malicious": malicious_count,
                "suspicious": suspicious_count,
                "clean": stats.get("clean", 0),
                "undetected": stats.get("undetected", 0),
                "scan_date": scan_datetime.isoformat() if scan_datetime else None,
                "reputation": attributes.get("reputation", 0),
                "categories": attributes.get("categories", {}),
                "fallback": False,
                "confidence": "high"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to parse URL report: {e}")
            return self._create_fallback_response("url_report", {"parse_error": str(e)})
    
    def _parse_file_report(self, data: dict) -> Dict:
        """Parse VirusTotal file report"""
        try:
            attributes = data.get("data", {}).get("attributes", {})
            stats = attributes.get("last_analysis_stats", {})
            
            total_engines = sum(stats.values())
            malicious_count = stats.get("malicious", 0)
            suspicious_count = stats.get("suspicious", 0)
            
            risk_score = 0.0
            if total_engines > 0:
                risk_score = (malicious_count + suspicious_count * 0.5) / total_engines
            
            return {
                "sha256": attributes.get("sha256"),
                "md5": attributes.get("md5"),
                "file_type": attributes.get("type_description"),
                "file_size": attributes.get("size"),
                "risk_score": round(risk_score, 3),
                "total_engines": total_engines,
                "malicious": malicious_count,
                "suspicious": suspicious_count,
                "clean": stats.get("clean", 0),
                "undetected": stats.get("undetected", 0),
                "scan_date": attributes.get("last_analysis_date"),
                "names": attributes.get("names", []),
                "fallback": False,
                "confidence": "high"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to parse file report: {e}")
            return self._create_fallback_response("file_hash", {"parse_error": str(e)})
    
    async def get_api_quota(self) -> Dict:
        """Get API quota information with fallback"""
        try:
            if not self.is_healthy or not self.client:
                return {"error": "VirusTotal unavailable", "fallback": True}
            
            # Try one of the stable endpoints instead of /users/self
            response = await self.client.get(
                f"{self.base_url}/domains/google.com",
                timeout=10.0
            )
            
            if response.status_code == 200:
                return {
                    "status": "available",
                    "remaining_requests": self.rate_limit - len(self.request_times),
                    "rate_limit": self.rate_limit,
                    "fallback": False
                }
            else:
                return {"error": f"HTTP {response.status_code}", "fallback": True}
                
        except Exception as e:
            return {"error": str(e), "fallback": True}
    
    async def health_check(self) -> Dict:
        """Comprehensive health check with stable endpoints"""
        try:
            if not self.api_key:
                return {
                    "status": "not_configured", 
                    "error": "API key not set",
                    "fallback": True
                }
            
            if not self.client:
                return {
                    "status": "not_initialized", 
                    "error": "Client not initialized",
                    "fallback": True
                }
            
            # Test with stable endpoints
            start_time = time.time()
            connection_success = await self._test_connection()
            response_time = (time.time() - start_time) * 1000
            
            if connection_success:
                self.is_healthy = True
                return {
                    "status": "connected",
                    "response_time_ms": round(response_time, 2),
                    "rate_limit_remaining": self.rate_limit - len(self.request_times),
                    "test_endpoints": self.test_endpoints,
                    "fallback": False
                }
            else:
                self.is_healthy = False
                return {
                    "status": "error",
                    "error": "Connection test failed",
                    "response_time_ms": round(response_time, 2),
                    "fallback": True
                }
                
        except Exception as e:
            self.is_healthy = False
            return {
                "status": "error", 
                "error": str(e),
                "fallback": True
            }

# Global VirusTotal instance
vt_api = VirusTotalAPI()
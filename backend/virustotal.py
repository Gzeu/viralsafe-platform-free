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
    """VirusTotal API integration with smart health monitoring via real scans"""
    
    def __init__(self):
        self.base_url = settings.VIRUSTOTAL_BASE_URL
        self.api_key = settings.VIRUSTOTAL_API_KEY
        self.rate_limit = settings.VIRUSTOTAL_RATE_LIMIT
        self.request_times = []  # Track request timestamps for rate limiting
        self.client: Optional[httpx.AsyncClient] = None
        
        # Smart health tracking - updated only when real scans happen
        self.health_cache = {
            "status": "unknown",
            "last_check": None,
            "last_successful_scan": None,
            "consecutive_failures": 0,
            "total_scans": 0,
            "successful_scans": 0
        }
        
        # Stable test endpoints for initialization only
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
                self.health_cache["status"] = "not_configured"
                return False
            
            self.client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "x-apikey": self.api_key,
                    "User-Agent": "ViralSafe/1.0"
                }
            )
            
            # One-time connection test during initialization only
            connection_success = await self._test_connection_once()
            
            if connection_success:
                logger.info("✅ VirusTotal API initialized successfully")
                self.health_cache["status"] = "connected"
                self.health_cache["last_check"] = datetime.utcnow().isoformat()
                return True
            else:
                logger.warning("⚠️ VirusTotal API connection failed during init - will retry on first scan")
                self.health_cache["status"] = "init_failed"
                return False
                
        except Exception as e:
            logger.error(f"❌ VirusTotal API initialization failed: {e}")
            self.health_cache["status"] = "error"
            self.health_cache["error"] = str(e)
            return False
    
    async def _test_connection_once(self) -> bool:
        """Test connection using stable endpoints - ONLY during initialization"""
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
    
    def _update_health_from_scan(self, success: bool, error_msg: str = None):
        """Update health status based on real scan results"""
        now = datetime.utcnow().isoformat()
        
        self.health_cache["last_check"] = now
        self.health_cache["total_scans"] += 1
        
        if success:
            self.health_cache["status"] = "connected"
            self.health_cache["last_successful_scan"] = now
            self.health_cache["successful_scans"] += 1
            self.health_cache["consecutive_failures"] = 0
            
            # Remove error if it existed
            if "error" in self.health_cache:
                del self.health_cache["error"]
                
            logger.info("✅ VirusTotal health updated: Connected (via real scan)")
        else:
            self.health_cache["consecutive_failures"] += 1
            
            # Determine status based on failure pattern
            if self.health_cache["consecutive_failures"] >= 3:
                self.health_cache["status"] = "error"
            else:
                self.health_cache["status"] = "degraded"
            
            if error_msg:
                self.health_cache["error"] = error_msg
            
            logger.warning(f"⚠️ VirusTotal health updated: {self.health_cache['status']} (consecutive failures: {self.health_cache['consecutive_failures']})")
    
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
        """Submit URL for scanning with health status update"""
        scan_success = False
        error_msg = None
        
        try:
            if not self.client:
                error_msg = "Client not initialized"
                logger.warning("⚠️ VirusTotal client not initialized - skipping URL scan")
                return self._create_fallback_response("url_scan", {"url": url, "error": error_msg})
            
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
                
                scan_success = True
                logger.info(f"✅ URL scan submitted: {scan_id}")
                
                return {
                    "scan_id": scan_id, 
                    "url": url, 
                    "submitted_at": datetime.utcnow().isoformat(),
                    "status": "submitted",
                    "fallback": False
                }
            else:
                error_msg = f"HTTP {response.status_code}"
                logger.error(f"❌ URL scan failed: {error_msg}")
                return self._create_fallback_response("url_scan", {"url": url, "error": error_msg})
                
        except asyncio.TimeoutError:
            error_msg = "timeout"
            logger.error(f"⏰ URL scan timeout for: {url}")
            return self._create_fallback_response("url_scan", {"url": url, "error": error_msg})
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ URL scan error: {e}")
            return self._create_fallback_response("url_scan", {"url": url, "error": error_msg})
        finally:
            # Update health status based on scan result
            self._update_health_from_scan(scan_success, error_msg)
    
    async def get_url_report(self, url: str) -> Optional[Dict]:
        """Get URL analysis report with health status update"""
        scan_success = False
        error_msg = None
        
        try:
            if not self.client:
                error_msg = "Client not initialized"
                logger.warning("⚠️ VirusTotal client not initialized - using fallback analysis")
                return self._create_fallback_response("url_report", {"url": url, "error": error_msg})
            
            await self._rate_limit_check()
            
            # Create URL ID for lookup
            url_id = self._get_url_id(url)
            
            response = await self.client.get(
                f"{self.base_url}/urls/{url_id}",
                timeout=30.0
            )
            
            if response.status_code == 200:
                scan_success = True
                return self._parse_url_report(response.json())
            elif response.status_code == 404:
                # URL not found, submit for scanning
                logger.info(f"🔍 URL not found in VT database, submitting for scan: {url}")
                await self.scan_url(url)  # This will update health status
                return self._create_fallback_response("url_report", {"url": url, "status": "not_found"})
            else:
                error_msg = f"HTTP {response.status_code}"
                logger.error(f"❌ URL report failed: {error_msg}")
                return self._create_fallback_response("url_report", {"url": url, "error": error_msg})
                
        except asyncio.TimeoutError:
            error_msg = "timeout"
            logger.error(f"⏰ URL report timeout for: {url}")
            return self._create_fallback_response("url_report", {"url": url, "error": error_msg})
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ URL report error: {e}")
            return self._create_fallback_response("url_report", {"url": url, "error": error_msg})
        finally:
            # Update health status only if we made an actual request (not for 404 case handled by scan_url)
            if error_msg or scan_success:
                self._update_health_from_scan(scan_success, error_msg)
    
    async def scan_file_hash(self, file_hash: str) -> Optional[Dict]:
        """Get file hash analysis report with health status update"""
        scan_success = False
        error_msg = None
        
        try:
            if not self.client:
                error_msg = "Client not initialized"
                logger.warning("⚠️ VirusTotal client not initialized - using fallback analysis")
                return self._create_fallback_response("file_hash", {"hash": file_hash, "error": error_msg})
            
            await self._rate_limit_check()
            
            response = await self.client.get(
                f"{self.base_url}/files/{file_hash}",
                timeout=30.0
            )
            
            if response.status_code == 200:
                scan_success = True
                return self._parse_file_report(response.json())
            elif response.status_code == 404:
                # Set scan_success = True because the API call worked, just no data
                scan_success = True
                logger.info(f"🔍 File hash not found in VT database: {file_hash}")
                return self._create_fallback_response("file_hash", {"hash": file_hash, "status": "not_found"})
            else:
                error_msg = f"HTTP {response.status_code}"
                logger.error(f"❌ File hash report failed: {error_msg}")
                return self._create_fallback_response("file_hash", {"hash": file_hash, "error": error_msg})
                
        except asyncio.TimeoutError:
            error_msg = "timeout"
            logger.error(f"⏰ File hash timeout for: {file_hash}")
            return self._create_fallback_response("file_hash", {"hash": file_hash, "error": error_msg})
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ File hash error: {e}")
            return self._create_fallback_response("file_hash", {"hash": file_hash, "error": error_msg})
        finally:
            # Update health status based on scan result
            self._update_health_from_scan(scan_success, error_msg)
    
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
        """Get API quota information from cached health data"""
        return {
            "status": self.health_cache["status"],
            "remaining_requests": max(0, self.rate_limit - len(self.request_times)),
            "rate_limit": self.rate_limit,
            "total_scans": self.health_cache["total_scans"],
            "successful_scans": self.health_cache["successful_scans"],
            "fallback": self.health_cache["status"] not in ["connected"]
        }
    
    async def health_check(self) -> Dict:
        """Smart health check using cached data from real scans"""
        now = datetime.utcnow()
        
        # Calculate success rate
        success_rate = 0.0
        if self.health_cache["total_scans"] > 0:
            success_rate = self.health_cache["successful_scans"] / self.health_cache["total_scans"]
        
        # Check if we have recent data
        last_check = self.health_cache.get("last_check")
        is_stale = False
        
        if last_check:
            last_check_dt = datetime.fromisoformat(last_check.replace('Z', '+00:00').replace('+00:00', ''))
            time_since_check = (now - last_check_dt).total_seconds()
            is_stale = time_since_check > 3600  # 1 hour
        
        # Prepare health response
        health_data = {
            "status": self.health_cache["status"],
            "last_check": self.health_cache["last_check"],
            "last_successful_scan": self.health_cache["last_successful_scan"],
            "total_scans": self.health_cache["total_scans"],
            "successful_scans": self.health_cache["successful_scans"],
            "success_rate": round(success_rate, 3),
            "consecutive_failures": self.health_cache["consecutive_failures"],
            "rate_limit_remaining": max(0, self.rate_limit - len(self.request_times)),
            "is_stale": is_stale,
            "monitoring_method": "smart_scan_based",
            "api_savings": "100% - No dedicated health checks!"
        }
        
        # Add error if present
        if "error" in self.health_cache:
            health_data["error"] = self.health_cache["error"]
        
        # Add message based on status
        if self.health_cache["status"] == "not_configured":
            health_data["message"] = "VirusTotal API key not configured"
        elif self.health_cache["status"] == "connected":
            health_data["message"] = "VirusTotal operational (verified via real scans)"
        elif self.health_cache["status"] == "degraded":
            health_data["message"] = "VirusTotal experiencing issues (degraded performance)"
        elif self.health_cache["status"] == "error":
            health_data["message"] = "VirusTotal unavailable (multiple consecutive failures)"
        else:
            health_data["message"] = "VirusTotal status unknown (no scans performed yet)"
        
        return health_data

# Global VirusTotal instance
vt_api = VirusTotalAPI()
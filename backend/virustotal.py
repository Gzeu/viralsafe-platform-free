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
    """VirusTotal API integration with rate limiting and error handling"""
    
    def __init__(self):
        self.base_url = settings.VIRUSTOTAL_BASE_URL
        self.api_key = settings.VIRUSTOTAL_API_KEY
        self.rate_limit = settings.VIRUSTOTAL_RATE_LIMIT
        self.request_times = []  # Track request timestamps for rate limiting
        self.client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self) -> bool:
        """Initialize HTTP client and validate API key"""
        try:
            if not self.api_key:
                logger.warning("VirusTotal API key not configured")
                return False
            
            self.client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "x-apikey": self.api_key,
                    "User-Agent": "ViralSafe/1.0"
                }
            )
            
            # Test API connection
            response = await self.client.get(f"{self.base_url}/users/self")
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"VirusTotal API initialized for user: {user_data.get('data', {}).get('attributes', {}).get('display_name', 'Unknown')}")
                return True
            elif response.status_code == 401:
                logger.error("VirusTotal API: Invalid API key")
                return False
            else:
                logger.error(f"VirusTotal API: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"VirusTotal API initialization failed: {e}")
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
                logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.request_times.append(now)
    
    async def scan_url(self, url: str) -> Optional[Dict]:
        """Submit URL for scanning"""
        try:
            if not self.client:
                logger.error("VirusTotal client not initialized")
                return None
            
            await self._rate_limit_check()
            
            # Submit URL for scanning
            scan_data = {"url": url}
            response = await self.client.post(f"{self.base_url}/urls", data=scan_data)
            
            if response.status_code == 200:
                result = response.json()
                scan_id = result.get("data", {}).get("id")
                
                logger.info(f"URL scan submitted: {scan_id}")
                return {"scan_id": scan_id, "url": url, "submitted_at": datetime.utcnow()}
            else:
                logger.error(f"URL scan failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"URL scan error: {e}")
            return None
    
    async def get_url_report(self, url: str) -> Optional[Dict]:
        """Get URL analysis report"""
        try:
            if not self.client:
                return None
            
            await self._rate_limit_check()
            
            # Create URL ID for lookup
            url_id = self._get_url_id(url)
            
            response = await self.client.get(f"{self.base_url}/urls/{url_id}")
            
            if response.status_code == 200:
                return self._parse_url_report(response.json())
            elif response.status_code == 404:
                # URL not found, submit for scanning
                logger.info(f"URL not found in VT database, submitting for scan: {url}")
                await self.scan_url(url)
                return None
            else:
                logger.error(f"URL report failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"URL report error: {e}")
            return None
    
    async def scan_file_hash(self, file_hash: str) -> Optional[Dict]:
        """Get file hash analysis report"""
        try:
            if not self.client:
                return None
            
            await self._rate_limit_check()
            
            response = await self.client.get(f"{self.base_url}/files/{file_hash}")
            
            if response.status_code == 200:
                return self._parse_file_report(response.json())
            elif response.status_code == 404:
                logger.info(f"File hash not found in VT database: {file_hash}")
                return None
            else:
                logger.error(f"File hash report failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"File hash error: {e}")
            return None
    
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
                "categories": attributes.get("categories", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to parse URL report: {e}")
            return {}
    
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
                "names": attributes.get("names", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to parse file report: {e}")
            return {}
    
    async def get_api_quota(self) -> Dict:
        """Get API quota information"""
        try:
            if not self.client:
                return {"error": "Client not initialized"}
            
            response = await self.client.get(f"{self.base_url}/users/self")
            
            if response.status_code == 200:
                data = response.json()
                quotas = data.get("data", {}).get("attributes", {}).get("quotas", {})
                
                return {
                    "api_requests_hourly": quotas.get("api_requests_hourly", {}),
                    "api_requests_daily": quotas.get("api_requests_daily", {}),
                    "api_requests_monthly": quotas.get("api_requests_monthly", {})
                }
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def health_check(self) -> Dict:
        """Check VirusTotal API health"""
        try:
            if not self.api_key:
                return {"status": "not_configured", "error": "API key not set"}
            
            if not self.client:
                return {"status": "not_initialized", "error": "Client not initialized"}
            
            # Simple API test
            start_time = time.time()
            response = await self.client.get(f"{self.base_url}/users/self")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                quotas = await self.get_api_quota()
                return {
                    "status": "connected",
                    "response_time_ms": round(response_time, 2),
                    "rate_limit_remaining": self.rate_limit - len(self.request_times),
                    "quotas": quotas
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}

# Global VirusTotal instance
vt_api = VirusTotalAPI()
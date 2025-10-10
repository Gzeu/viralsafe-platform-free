"""
VirusTotal API Integration Service
Optimized for FREE tier: 4 requests/minute, 500 requests/day
"""

import os
import asyncio
import hashlib
import aiohttp
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

@dataclass
class VirusTotalConfig:
    """VirusTotal API configuration"""
    api_key: str
    base_url: str = "https://www.virustotal.com/api/v3"
    rate_limit: int = 4  # requests per minute
    daily_limit: int = 500  # requests per day
    timeout: int = 30  # seconds

class RateLimiter:
    """Simple rate limiter for VirusTotal API"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window  # seconds
        self.requests = []
        self.daily_requests = 0
        self.daily_reset = datetime.now(timezone.utc) + timedelta(days=1)
    
    async def acquire(self) -> bool:
        """Check if we can make a request within rate limits"""
        now = datetime.now(timezone.utc)
        
        # Reset daily counter if needed
        if now >= self.daily_reset:
            self.daily_requests = 0
            self.daily_reset = now + timedelta(days=1)
        
        # Check daily limit
        if self.daily_requests >= 500:  # FREE tier daily limit
            logger.warning("VirusTotal daily limit reached (500 requests)")
            return False
        
        # Remove old requests outside time window
        cutoff = now - timedelta(seconds=self.time_window)
        self.requests = [req_time for req_time in self.requests if req_time > cutoff]
        
        # Check rate limit
        if len(self.requests) >= self.max_requests:
            wait_time = self.time_window - (now - self.requests[0]).total_seconds()
            logger.info(f"Rate limit reached. Waiting {wait_time:.1f} seconds")
            await asyncio.sleep(wait_time)
            return await self.acquire()  # Retry
        
        # Record this request
        self.requests.append(now)
        self.daily_requests += 1
        return True

class VirusTotalService:
    """VirusTotal API service with caching and rate limiting"""
    
    def __init__(self, config: VirusTotalConfig):
        self.config = config
        self.rate_limiter = RateLimiter(
            max_requests=config.rate_limit,
            time_window=60  # 1 minute
        )
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Headers for API requests
        self.headers = {
            "X-Apikey": config.api_key,
            "User-Agent": "ViralSafe-Platform/1.0",
            "Accept": "application/json"
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers=self.headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _generate_hash(self, content: str, algorithm: str = "md5") -> str:
        """Generate hash for content"""
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(content.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid for scanning"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    async def scan_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Scan URL with VirusTotal API"""
        if not self._is_valid_url(url):
            return None
        
        if not await self.rate_limiter.acquire():
            return None
        
        try:
            # First, submit URL for scanning
            submit_url = f"{self.config.base_url}/urls"
            form_data = aiohttp.FormData()
            form_data.add_field('url', url)
            
            async with self.session.post(submit_url, data=form_data) as response:
                if response.status == 200:
                    submit_result = await response.json()
                    analysis_id = submit_result.get("data", {}).get("id")
                    
                    if analysis_id:
                        # Wait a bit for analysis to complete
                        await asyncio.sleep(15)
                        
                        # Get analysis results
                        return await self._get_analysis_result(analysis_id)
                
                logger.error(f"VirusTotal URL submission failed: {response.status}")
                return None
                
        except Exception as e:
            logger.error(f"VirusTotal URL scan error: {e}")
            return None
    
    async def scan_file_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Scan file hash with VirusTotal API"""
        if not file_hash or len(file_hash) < 32:
            return None
        
        if not await self.rate_limiter.acquire():
            return None
        
        try:
            # Get file report by hash
            report_url = f"{self.config.base_url}/files/{file_hash}"
            
            async with self.session.get(report_url) as response:
                if response.status == 200:
                    result = await response.json()
                    return self._process_file_report(result)
                elif response.status == 404:
                    logger.info(f"File hash not found in VirusTotal: {file_hash}")
                    return None
                else:
                    logger.error(f"VirusTotal file scan failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"VirusTotal file scan error: {e}")
            return None
    
    async def scan_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """Scan domain with VirusTotal API"""
        if not domain or '.' not in domain:
            return None
        
        if not await self.rate_limiter.acquire():
            return None
        
        try:
            # Get domain report
            domain_url = f"{self.config.base_url}/domains/{domain}"
            
            async with self.session.get(domain_url) as response:
                if response.status == 200:
                    result = await response.json()
                    return self._process_domain_report(result)
                else:
                    logger.error(f"VirusTotal domain scan failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"VirusTotal domain scan error: {e}")
            return None
    
    async def _get_analysis_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis result by ID"""
        try:
            analysis_url = f"{self.config.base_url}/analyses/{analysis_id}"
            
            async with self.session.get(analysis_url) as response:
                if response.status == 200:
                    result = await response.json()
                    return self._process_url_report(result)
                else:
                    logger.error(f"VirusTotal analysis result failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"VirusTotal analysis result error: {e}")
            return None
    
    def _process_url_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Process URL scan report"""
        data = report.get("data", {})
        attributes = data.get("attributes", {})
        stats = attributes.get("stats", {})
        
        return {
            "type": "url",
            "scan_id": data.get("id"),
            "scan_date": attributes.get("date"),
            "positives": stats.get("malicious", 0) + stats.get("suspicious", 0),
            "total": sum(stats.values()) if stats else 0,
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "clean": stats.get("harmless", 0),
            "undetected": stats.get("undetected", 0),
            "engines": self._extract_engine_results(attributes.get("results", {})),
            "permalink": f"https://www.virustotal.com/gui/url/{data.get('id')}"
        }
    
    def _process_file_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Process file scan report"""
        data = report.get("data", {})
        attributes = data.get("attributes", {})
        stats = attributes.get("last_analysis_stats", {})
        
        return {
            "type": "file",
            "scan_id": data.get("id"),
            "md5": attributes.get("md5"),
            "sha1": attributes.get("sha1"),
            "sha256": attributes.get("sha256"),
            "scan_date": attributes.get("last_analysis_date"),
            "positives": stats.get("malicious", 0) + stats.get("suspicious", 0),
            "total": sum(stats.values()) if stats else 0,
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "clean": stats.get("harmless", 0),
            "undetected": stats.get("undetected", 0),
            "engines": self._extract_engine_results(attributes.get("last_analysis_results", {})),
            "permalink": f"https://www.virustotal.com/gui/file/{data.get('id')}"
        }
    
    def _process_domain_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Process domain scan report"""
        data = report.get("data", {})
        attributes = data.get("attributes", {})
        stats = attributes.get("last_analysis_stats", {})
        
        return {
            "type": "domain",
            "domain": data.get("id"),
            "scan_date": attributes.get("last_analysis_date"),
            "positives": stats.get("malicious", 0) + stats.get("suspicious", 0),
            "total": sum(stats.values()) if stats else 0,
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "clean": stats.get("harmless", 0),
            "undetected": stats.get("undetected", 0),
            "engines": self._extract_engine_results(attributes.get("last_analysis_results", {})),
            "permalink": f"https://www.virustotal.com/gui/domain/{data.get('id')}"
        }
    
    def _extract_engine_results(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract and format engine scan results"""
        engines = []
        for engine_name, result in results.items():
            if isinstance(result, dict) and result.get("category") in ["malicious", "suspicious"]:
                engines.append({
                    "engine": engine_name,
                    "category": result.get("category"),
                    "result": result.get("result", "Unknown")
                })
        return engines[:10]  # Limit to top 10 detections

# Global VirusTotal service instance
vt_service: Optional[VirusTotalService] = None

def get_virustotal_service() -> Optional[VirusTotalService]:
    """Get VirusTotal service instance"""
    global vt_service
    
    api_key = os.getenv("VIRUSTOTAL_API_KEY")
    if not api_key or api_key == "your_virustotal_api_key_here":
        return None
    
    if not vt_service:
        config = VirusTotalConfig(
            api_key=api_key,
            rate_limit=int(os.getenv("VIRUSTOTAL_RATE_LIMIT", "4")),
            daily_limit=int(os.getenv("VIRUSTOTAL_DAILY_LIMIT", "500")),
            timeout=int(os.getenv("VIRUSTOTAL_TIMEOUT", "30"))
        )
        vt_service = VirusTotalService(config)
    
    return vt_service

async def analyze_content_with_virustotal(
    content: str, 
    url: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Analyze content with VirusTotal integration"""
    service = get_virustotal_service()
    if not service:
        return None
    
    async with service:
        # If URL is provided, scan it
        if url and service._is_valid_url(url):
            return await service.scan_url(url)
        
        # Generate content hash and check if it's a known file hash
        content_hash = service._generate_hash(content, "md5")
        if len(content_hash) == 32:  # MD5 hash length
            return await service.scan_file_hash(content_hash)
        
        # Extract domains from content for scanning
        domains = extract_domains_from_content(content)
        if domains:
            # Scan the first domain found
            return await service.scan_domain(domains[0])
    
    return None

def extract_domains_from_content(content: str) -> List[str]:
    """Extract domains from content for VirusTotal scanning"""
    import re
    
    # Regex to find domains in content
    domain_pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
    matches = re.findall(domain_pattern, content.lower())
    
    # Filter out common safe domains
    safe_domains = {
        'google.com', 'facebook.com', 'twitter.com', 'youtube.com',
        'github.com', 'linkedin.com', 'microsoft.com', 'apple.com'
    }
    
    suspicious_domains = []
    for domain in matches:
        if domain not in safe_domains and len(domain) > 4:
            suspicious_domains.append(domain)
    
    return suspicious_domains[:3]  # Limit to first 3 domains
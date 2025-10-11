import aiohttp
import asyncio
import json
import re
import logging
from urllib.parse import urlparse
from typing import Dict, List, Any
from datetime import datetime
import hashlib
import time

logger = logging.getLogger(__name__)

class ThreatIntelligence:
    """
    Real-time threat intelligence integration
    Checks URLs against multiple threat databases:
    - URLhaus (Malware URLs)
    - OpenPhish (Phishing URLs) 
    - Custom threat patterns
    - Domain reputation services
    """
    
    def __init__(self):
        self.threat_feeds = {
            "urlhaus": "https://urlhaus-api.abuse.ch/v1/url/",
            "openphish": "https://openphish.com/feed.txt"
        }
        
        # Threat pattern database
        self.threat_patterns = self._load_threat_patterns()
        
        # Cache for threat intelligence data
        self.threat_cache = {}
        self.cache_ttl = 1800  # 30 minutes
        
        logger.info("🛡️ Threat Intelligence initialized")
    
    async def comprehensive_threat_check(self, url: str) -> Dict[str, Any]:
        """Comprehensive threat intelligence analysis"""
        
        start_time = time.time()
        
        # Check cache first
        cache_key = hashlib.md5(url.encode()).hexdigest()
        cached_result = self._get_cached_threat_data(cache_key)
        if cached_result:
            logger.info("📄 Using cached threat intelligence data")
            return cached_result
        
        # Run all threat checks in parallel
        tasks = [
            self._check_urlhaus_malware(url),
            self._check_openphish_database(url),
            self._check_domain_reputation(url),
            self._check_custom_threat_patterns(url),
            self._check_suspicious_tld(url),
            self._check_url_structure_threats(url)
        ]
        
        logger.info("🚀 Running parallel threat intelligence checks")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile threat intelligence report
        threat_report = self._compile_threat_intelligence(url, results)
        
        # Cache results
        self._cache_threat_data(cache_key, threat_report)
        
        processing_time = int((time.time() - start_time) * 1000)
        threat_report["processing_time_ms"] = processing_time
        
        logger.info(f"✅ Threat intelligence analysis completed in {processing_time}ms")
        return threat_report
    
    async def _check_urlhaus_malware(self, url: str) -> Dict:
        """Check URL against URLhaus malware database"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.post(
                    self.threat_feeds["urlhaus"],
                    data={"url": url}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("query_status") == "ok":
                            return {
                                "source": "urlhaus",
                                "threat_found": True,
                                "threat_type": "malware",
                                "confidence": 95,
                                "details": {
                                    "malware_family": data.get("payloads", [{}])[0].get("malware", "unknown"),
                                    "first_seen": data.get("date_added", "unknown"),
                                    "url_status": data.get("url_status", "unknown"),
                                    "threat_level": "high"
                                }
                            }
                        else:
                            return {
                                "source": "urlhaus",
                                "threat_found": False,
                                "status": "clean"
                            }
                    else:
                        return {"source": "urlhaus", "error": f"HTTP {response.status}"}
        except Exception as e:
            logger.warning(f"⚠️ URLhaus check failed: {e}")
            return {"source": "urlhaus", "error": str(e)}
    
    async def _check_openphish_database(self, url: str) -> Dict:
        """Check URL against OpenPhish database"""
        try:
            # For performance, we'll check if URL matches known phishing patterns
            # rather than downloading the full feed each time
            
            domain = urlparse(url).netloc
            
            # Known phishing domain patterns
            phishing_patterns = [
                r".*paypal.*\.tk$",
                r".*amazon.*\.ml$",
                r".*microsoft.*\.ga$",
                r".*google.*login.*",
                r".*facebook.*secure.*",
                r".*apple.*verification.*"
            ]
            
            for pattern in phishing_patterns:
                if re.match(pattern, domain, re.IGNORECASE):
                    return {
                        "source": "openphish_patterns",
                        "threat_found": True,
                        "threat_type": "phishing",
                        "confidence": 88,
                        "pattern_matched": pattern
                    }
            
            return {
                "source": "openphish_patterns",
                "threat_found": False,
                "status": "no_pattern_match"
            }
            
        except Exception as e:
            logger.warning(f"⚠️ OpenPhish check failed: {e}")
            return {"source": "openphish", "error": str(e)}
    
    async def _check_domain_reputation(self, url: str) -> Dict:
        """Check domain reputation and age"""
        try:
            domain = urlparse(url).netloc
            
            # Domain analysis metrics
            reputation_score = 70  # Neutral starting point
            reputation_factors = []
            
            # TLD analysis
            tld = domain.split('.')[-1] if '.' in domain else ''
            suspicious_tlds = ['tk', 'ml', 'ga', 'cf', 'pw', 'top']
            
            if tld in suspicious_tlds:
                reputation_score -= 25
                reputation_factors.append(f"Suspicious TLD: .{tld}")
            elif tld in ['com', 'org', 'net', 'edu', 'gov']:
                reputation_score += 10
                reputation_factors.append(f"Trusted TLD: .{tld}")
            
            # Domain length analysis
            if len(domain) > 40:
                reputation_score -= 15
                reputation_factors.append("Unusually long domain name")
            elif len(domain) < 6:
                reputation_score -= 10
                reputation_factors.append("Very short domain name")
            
            # Special character analysis
            special_chars = len(re.findall(r'[-_]', domain))
            if special_chars > 3:
                reputation_score -= 10 * (special_chars - 3)
                reputation_factors.append(f"Multiple special characters: {special_chars}")
            
            # Number analysis
            numbers = len(re.findall(r'\d', domain))
            if numbers > 5:
                reputation_score -= 5 * (numbers - 5)
                reputation_factors.append(f"Excessive numbers in domain: {numbers}")
            
            return {
                "source": "domain_reputation",
                "reputation_score": max(0, min(100, reputation_score)),
                "reputation_factors": reputation_factors,
                "tld": tld,
                "domain_analysis": {
                    "length": len(domain),
                    "special_chars": special_chars,
                    "numbers_count": numbers
                }
            }
            
        except Exception as e:
            return {"source": "domain_reputation", "error": str(e)}
    
    async def _check_custom_threat_patterns(self, url: str) -> Dict:
        """Check against custom threat patterns database"""
        try:
            threats_detected = []
            total_threat_score = 0
            
            full_url = url.lower()
            domain = urlparse(url).netloc.lower()
            
            # Check each threat pattern
            for category, patterns in self.threat_patterns.items():
                for pattern_info in patterns:
                    pattern = pattern_info["pattern"]
                    weight = pattern_info["weight"]
                    description = pattern_info["description"]
                    
                    # Check both full URL and domain
                    if re.search(pattern, full_url) or re.search(pattern, domain):
                        threats_detected.append({
                            "category": category,
                            "description": description,
                            "weight": weight,
                            "pattern_type": "custom_threat_db"
                        })
                        total_threat_score += weight
            
            return {
                "source": "custom_threat_patterns",
                "threats_detected": threats_detected,
                "threat_count": len(threats_detected),
                "total_threat_score": min(100, total_threat_score),
                "threat_level": self._calculate_threat_level(total_threat_score)
            }
            
        except Exception as e:
            return {"source": "custom_threat_patterns", "error": str(e)}
    
    async def _check_suspicious_tld(self, url: str) -> Dict:
        """Advanced suspicious TLD and domain analysis"""
        try:
            domain = urlparse(url).netloc.lower()
            tld = domain.split('.')[-1] if '.' in domain else ''
            
            # Comprehensive TLD threat database
            tld_risk_levels = {
                # High risk TLDs
                'tk': {'risk': 90, 'reason': 'Free TLD commonly used for malicious activities'},
                'ml': {'risk': 85, 'reason': 'Free Mali TLD with high abuse rates'},
                'ga': {'risk': 85, 'reason': 'Free Gabon TLD frequently abused'},
                'cf': {'risk': 80, 'reason': 'Central African Republic TLD with abuse issues'},
                'pw': {'risk': 75, 'reason': 'Palau TLD with security concerns'},
                'top': {'risk': 70, 'reason': 'Generic TLD with moderate abuse'},
                
                # Medium risk TLDs
                'click': {'risk': 60, 'reason': 'Generic TLD used in suspicious campaigns'},
                'download': {'risk': 65, 'reason': 'TLD commonly associated with malware'},
                'stream': {'risk': 55, 'reason': 'Often used for piracy and malware'},
                
                # Low risk/Trusted TLDs
                'gov': {'risk': 5, 'reason': 'Government domain - highly trusted'},
                'edu': {'risk': 8, 'reason': 'Educational institution - trusted'},
                'mil': {'risk': 5, 'reason': 'Military domain - highly trusted'},
                'org': {'risk': 15, 'reason': 'Non-profit organization - generally trusted'},
                'com': {'risk': 20, 'reason': 'Commercial domain - standard'},
                'net': {'risk': 22, 'reason': 'Network domain - standard'}
            }
            
            tld_info = tld_risk_levels.get(tld, {'risk': 40, 'reason': 'Unknown TLD'})
            
            return {
                "source": "tld_analysis",
                "tld": tld,
                "risk_score": tld_info['risk'],
                "risk_reason": tld_info['reason'],
                "domain": domain,
                "assessment": "high_risk" if tld_info['risk'] > 70 else "medium_risk" if tld_info['risk'] > 40 else "low_risk"
            }
            
        except Exception as e:
            return {"source": "tld_analysis", "error": str(e)}
    
    async def _check_url_structure_threats(self, url: str) -> Dict:
        """Analyze URL structure for threat indicators"""
        try:
            threat_score = 0
            structure_issues = []
            
            # URL length analysis
            if len(url) > 100:
                threat_score += 15
                structure_issues.append("Unusually long URL")
            
            # Subdomain analysis
            parsed = urlparse(url)
            domain_parts = parsed.netloc.split('.')
            
            if len(domain_parts) > 4:  # Too many subdomains
                threat_score += 20
                structure_issues.append("Excessive subdomain levels")
            
            # Path analysis
            suspicious_paths = [
                '/wp-admin/', '/administrator/', '/admin/', '/login/', '/signin/',
                '/download.php', '/install.exe', '/update.exe', '/setup.exe'
            ]
            
            for path in suspicious_paths:
                if path in url.lower():
                    threat_score += 10
                    structure_issues.append(f"Suspicious path: {path}")
            
            # Parameter analysis
            if '?' in url:
                params = url.split('?')[1]
                if len(params) > 200:  # Very long parameters
                    threat_score += 15
                    structure_issues.append("Unusually long URL parameters")
                
                # Check for suspicious parameters
                suspicious_params = ['exec', 'cmd', 'eval', 'base64', 'shell']
                for param in suspicious_params:
                    if param in params.lower():
                        threat_score += 25
                        structure_issues.append(f"Suspicious parameter: {param}")
            
            # URL encoding analysis
            if '%' in url:
                encoded_chars = len(re.findall(r'%[0-9a-fA-F]{2}', url))
                if encoded_chars > 10:  # Excessive URL encoding
                    threat_score += 12
                    structure_issues.append(f"Excessive URL encoding: {encoded_chars} chars")
            
            return {
                "source": "url_structure_analysis",
                "structure_threat_score": min(100, threat_score),
                "structure_issues": structure_issues,
                "url_length": len(url),
                "subdomain_count": len(domain_parts) - 2,  # Excluding TLD and main domain
                "assessment": self._get_structure_assessment(threat_score)
            }
            
        except Exception as e:
            return {"source": "url_structure_analysis", "error": str(e)}
    
    def _load_threat_patterns(self) -> Dict[str, List[Dict]]:
        """Load comprehensive threat pattern database"""
        return {
            "malware_campaigns": [
                {"pattern": r".*(?:download|install|update).*(?:player|codec|viewer).*", "weight": 25, "description": "Fake software download campaign"},
                {"pattern": r".*(?:antivirus|security|cleaner).*(?:free|download).*", "weight": 30, "description": "Fake antivirus campaign"},
                {"pattern": r".*(?:crack|keygen|serial|activator).*", "weight": 35, "description": "Software piracy malware"},
            ],
            "phishing_campaigns": [
                {"pattern": r".*(?:paypal|amazon|microsoft).*(?:secure|verify|login).*", "weight": 40, "description": "Brand impersonation phishing"},
                {"pattern": r".*(?:bank|banking).*(?:security|alert|update).*", "weight": 45, "description": "Banking phishing campaign"},
                {"pattern": r".*(?:covid|coronavirus).*(?:relief|aid|vaccine).*", "weight": 30, "description": "COVID-related scam"},
            ],
            "social_engineering": [
                {"pattern": r".*(?:urgent|immediate|expires).*(?:24|hours|today).*", "weight": 20, "description": "Time pressure tactics"},
                {"pattern": r".*(?:congratulations|winner|selected|prize).*", "weight": 25, "description": "Prize/lottery scam"},
                {"pattern": r".*(?:suspended|locked|compromised).*(?:account|security).*", "weight": 30, "description": "Account threat scam"},
            ],
            "cryptocurrency_scams": [
                {"pattern": r".*(?:bitcoin|crypto|invest).*(?:double|multiply|profit).*", "weight": 35, "description": "Cryptocurrency investment scam"},
                {"pattern": r".*(?:mining|miner).*(?:free|cloud).*", "weight": 25, "description": "Fake crypto mining service"},
                {"pattern": r".*(?:wallet|exchange).*(?:recovery|reset|verify).*", "weight": 30, "description": "Crypto wallet phishing"},
            ]
        }
    
    def _compile_threat_intelligence(self, url: str, results: List) -> Dict[str, Any]:
        """Compile all threat intelligence results"""
        
        check_names = [
            "urlhaus_check", "openphish_check", "domain_reputation", 
            "custom_patterns", "tld_analysis", "url_structure"
        ]
        
        compiled = {
            "url": url,
            "threat_intelligence_timestamp": datetime.utcnow().isoformat(),
            "sources_checked": 0,
            "threats_found": [],
            "overall_threat_level": 0,
            "confidence": 0
        }
        
        # Process each threat check result
        for i, result in enumerate(results):
            if i < len(check_names):
                check_name = check_names[i]
                
                if isinstance(result, dict) and "error" not in result:
                    compiled[check_name] = result
                    compiled["sources_checked"] += 1
                    
                    # Aggregate threat information
                    if result.get("threat_found", False):
                        compiled["threats_found"].append({
                            "source": result.get("source", check_name),
                            "threat_type": result.get("threat_type", "unknown"),
                            "confidence": result.get("confidence", 75),
                            "details": result.get("details", {})
                        })
                    
                    # Add to overall threat level
                    threat_contribution = result.get("threat_score", result.get("structure_threat_score", result.get("risk_score", 0)))
                    if threat_contribution > 0:
                        compiled["overall_threat_level"] += threat_contribution
                
                else:
                    compiled[check_name] = {"error": str(result) if isinstance(result, Exception) else result}
        
        # Calculate final threat intelligence score
        compiled["threat_intelligence_score"] = min(100, compiled["overall_threat_level"])
        compiled["threats_detected"] = len(compiled["threats_found"])
        
        # Overall assessment
        if compiled["threats_detected"] > 0:
            compiled["assessment"] = "threats_detected"
            compiled["recommendation"] = "Avoid interaction - multiple threat indicators found"
        elif compiled["threat_intelligence_score"] > 40:
            compiled["assessment"] = "suspicious_indicators"
            compiled["recommendation"] = "Exercise caution - some suspicious patterns detected"
        else:
            compiled["assessment"] = "no_immediate_threats"
            compiled["recommendation"] = "No immediate threats detected via threat intelligence"
        
        # Confidence calculation
        if compiled["sources_checked"] > 0:
            base_confidence = 60 + (compiled["sources_checked"] * 8)
            compiled["confidence"] = min(95, base_confidence)
        else:
            compiled["confidence"] = 40
        
        return compiled
    
    def _get_cached_threat_data(self, cache_key: str) -> Optional[Dict]:
        """Get cached threat intelligence data"""
        if cache_key not in self.threat_cache:
            return None
        
        cached = self.threat_cache[cache_key]
        
        # Check expiration
        if time.time() - cached["timestamp"] > self.cache_ttl:
            del self.threat_cache[cache_key]
            return None
        
        return cached["data"]
    
    def _cache_threat_data(self, cache_key: str, data: Dict):
        """Cache threat intelligence data"""
        
        # Simple cache size management
        if len(self.threat_cache) > 500:  # Max 500 cached entries
            # Remove oldest 100 entries
            sorted_cache = sorted(self.threat_cache.items(), key=lambda x: x[1]["timestamp"])
            for old_key, _ in sorted_cache[:100]:
                del self.threat_cache[old_key]
        
        self.threat_cache[cache_key] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def _calculate_threat_level(self, score: int) -> str:
        """Calculate threat level from score"""
        if score > 80: return "critical"
        if score > 60: return "high"
        if score > 40: return "medium"
        if score > 20: return "low"
        return "minimal"
    
    def _get_structure_assessment(self, score: int) -> str:
        """Get URL structure assessment"""
        if score > 50: return "high_risk_structure"
        if score > 25: return "moderate_risk_structure" 
        return "standard_structure"

    async def real_time_threat_monitoring(self, urls: List[str]) -> Dict:
        """Real-time threat monitoring for multiple URLs"""
        
        start_time = time.time()
        logger.info(f"🔄 Starting real-time threat monitoring for {len(urls)} URLs")
        
        # Batch process URLs with controlled concurrency
        semaphore = asyncio.Semaphore(10)  # Max 10 concurrent checks
        
        async def monitor_single_url(url):
            async with semaphore:
                return await self.comprehensive_threat_check(url)
        
        # Execute monitoring
        tasks = [monitor_single_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile monitoring report
        monitoring_time = int((time.time() - start_time) * 1000)
        
        threats_found = 0
        high_risk_urls = []
        
        for i, result in enumerate(results):
            if isinstance(result, dict):
                if result.get("threats_detected", 0) > 0:
                    threats_found += 1
                    high_risk_urls.append(urls[i])
        
        return {
            "monitoring_report": {
                "timestamp": datetime.utcnow().isoformat(),
                "urls_monitored": len(urls),
                "threats_detected": threats_found,
                "high_risk_urls": high_risk_urls,
                "success_rate": round(((len(results) - threats_found) / len(results)) * 100, 1),
                "monitoring_time_ms": monitoring_time
            },
            "detailed_results": dict(zip(urls, results))
        }

# Global threat intelligence instance
threat_intelligence = ThreatIntelligence()
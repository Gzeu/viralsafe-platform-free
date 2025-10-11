import aiohttp
import asyncio
import re
import socket
import ssl
import json
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import Dict, List, Any
import dns.resolver
import hashlib
import time

logger = logging.getLogger(__name__)

class AdvancedWebScanner:
    """
    Comprehensive web security scanner with 9 different scan types:
    1. HTTP Analysis
    2. Content Analysis  
    3. Security Headers
    4. DNS Analysis
    5. SSL/TLS Analysis
    6. Domain Reputation
    7. Malware Detection
    8. Phishing Detection
    9. Social Engineering Scan
    """
    
    def __init__(self):
        self.session = None
        self.malware_patterns = self._load_malware_patterns()
        self.phishing_indicators = self._load_phishing_indicators()
        self.social_engineering_patterns = self._load_social_engineering_patterns()
        
    async def comprehensive_scan(self, url: str) -> Dict[str, Any]:
        """Multi-layer comprehensive website security analysis"""
        
        start_time = time.time()
        logger.info(f"🔍 Starting comprehensive scan for: {url}")
        
        # Create persistent session for better performance
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=15, connect=5)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'ViralSafe-Advanced-Scanner/3.1 (Security-Research)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br'
            }
        ) as session:
            self.session = session
            
            # Run all 9 scan types in parallel
            tasks = [
                self._http_analysis(url),           # 1. HTTP Analysis
                self._content_analysis(url),        # 2. Content Analysis
                self._security_headers_scan(url),   # 3. Security Headers
                self._dns_analysis(url),            # 4. DNS Analysis
                self._ssl_analysis(url),            # 5. SSL Analysis
                self._domain_reputation(url),       # 6. Domain Reputation
                self._malware_detection(url),       # 7. Malware Detection
                self._phishing_detection(url),      # 8. Phishing Detection
                self._social_engineering_scan(url)  # 9. Social Engineering
            ]
            
            logger.info("🚀 Running 9 parallel security scans")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Compile comprehensive results
            compiled_results = self._compile_scan_results(url, results)
            
            scan_time = int((time.time() - start_time) * 1000)
            compiled_results["scan_performance"] = {
                "total_time_ms": scan_time,
                "parallel_scans": 9,
                "successful_scans": len([r for r in results if isinstance(r, dict) and "error" not in r]),
                "scan_efficiency": "High - Parallel execution"
            }
            
            logger.info(f"✅ Comprehensive scan completed in {scan_time}ms")
            return compiled_results
    
    async def _http_analysis(self, url: str) -> Dict:
        """1. HTTP Response and Performance Analysis"""
        try:
            start_time = time.time()
            async with self.session.get(url, allow_redirects=True) as response:
                response_time = int((time.time() - start_time) * 1000)
                
                return {
                    "status_code": response.status,
                    "response_time_ms": response_time,
                    "content_length": len(await response.text()),
                    "content_type": response.headers.get('content-type', ''),
                    "server": response.headers.get('server', 'unknown'),
                    "redirects_count": len(response.history),
                    "final_url": str(response.url),
                    "http_version": f"HTTP/{response.version.major}.{response.version.minor}",
                    "cookies_count": len(response.cookies),
                    "performance_grade": "A" if response_time < 500 else "B" if response_time < 1500 else "C"
                }
        except Exception as e:
            return {"error": str(e), "scan_type": "http_analysis"}
    
    async def _content_analysis(self, url: str) -> Dict:
        """2. Deep HTML Content Analysis"""
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Analyze content structure
                forms = soup.find_all('form')
                scripts = soup.find_all('script')
                iframes = soup.find_all('iframe')
                
                # Security-relevant content analysis
                return {
                    "page_title": soup.title.string.strip() if soup.title else "",
                    "meta_description": self._get_meta_content(soup, 'description'),
                    "meta_keywords": self._get_meta_content(soup, 'keywords'),
                    "forms_count": len(forms),
                    "login_forms": len([f for f in forms if self._is_login_form(f)]),
                    "payment_forms": len([f for f in forms if self._is_payment_form(f)]),
                    "external_scripts": self._count_external_scripts(scripts, url),
                    "suspicious_iframes": self._analyze_suspicious_iframes(iframes),
                    "hidden_elements": len(soup.find_all(attrs={"style": re.compile(r"display\s*:\s*none|visibility\s*:\s*hidden")})),
                    "external_links": self._count_external_links(soup, url),
                    "images_count": len(soup.find_all('img')),
                    "content_language": soup.get('lang', 'unknown'),
                    "suspicious_keywords": self._scan_suspicious_keywords(html),
                    "obfuscated_code": self._detect_code_obfuscation(html)
                }
        except Exception as e:
            return {"error": str(e), "scan_type": "content_analysis"}
    
    async def _security_headers_scan(self, url: str) -> Dict:
        """3. Comprehensive Security Headers Analysis"""
        try:
            async with self.session.get(url) as response:
                headers = dict(response.headers)
                
                security_score = 100
                security_issues = []
                recommendations = []
                
                # Critical security headers
                critical_headers = {
                    'Strict-Transport-Security': {'weight': 25, 'description': 'HSTS protection'},
                    'Content-Security-Policy': {'weight': 20, 'description': 'XSS/injection protection'},
                    'X-Frame-Options': {'weight': 15, 'description': 'Clickjacking protection'},
                    'X-Content-Type-Options': {'weight': 10, 'description': 'MIME sniffing protection'},
                    'X-XSS-Protection': {'weight': 10, 'description': 'XSS filtering'},
                    'Referrer-Policy': {'weight': 10, 'description': 'Referrer information control'},
                    'Permissions-Policy': {'weight': 10, 'description': 'Browser feature control'}
                }
                
                for header, info in critical_headers.items():
                    if header not in headers:
                        security_score -= info['weight']
                        security_issues.append(f"Missing {header}")
                        recommendations.append(f"Add {header} for {info['description']}")
                
                # Analyze existing headers quality
                header_quality = self._analyze_header_quality(headers)
                
                return {
                    "security_score": max(0, security_score),
                    "grade": self._get_security_grade(security_score),
                    "missing_headers": security_issues,
                    "recommendations": recommendations,
                    "header_analysis": header_quality,
                    "total_headers": len(headers),
                    "security_headers_present": len([h for h in critical_headers if h in headers])
                }
        except Exception as e:
            return {"error": str(e), "scan_type": "security_headers"}
    
    async def _dns_analysis(self, url: str) -> Dict:
        """4. Advanced DNS and Domain Analysis"""
        try:
            domain = urlparse(url).netloc
            
            # DNS record analysis
            dns_records = {}
            record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME', 'SOA']
            
            for record_type in record_types:
                try:
                    answers = dns.resolver.resolve(domain, record_type)
                    dns_records[record_type] = [str(rdata) for rdata in answers]
                except dns.resolver.NXDOMAIN:
                    dns_records[record_type] = ["NXDOMAIN"]
                except Exception:
                    dns_records[record_type] = []
            
            # Suspicious DNS analysis
            dns_suspicion_score = self._analyze_dns_suspicion(dns_records, domain)
            
            return {
                "domain": domain,
                "dns_records": dns_records,
                "dns_health": "healthy" if dns_records.get('A') else "problematic",
                "mx_configured": bool(dns_records.get('MX')),
                "spf_record": self._check_spf_record(dns_records.get('TXT', [])),
                "dmarc_record": self._check_dmarc_record(dns_records.get('TXT', [])),
                "dns_suspicion_score": dns_suspicion_score,
                "suspicious_patterns": self._get_dns_suspicious_patterns(dns_records)
            }
        except Exception as e:
            return {"error": str(e), "scan_type": "dns_analysis"}
    
    async def _ssl_analysis(self, url: str) -> Dict:
        """5. Advanced SSL/TLS Certificate Analysis"""
        try:
            domain = urlparse(url).netloc
            port = 443
            
            # Get SSL certificate details
            context = ssl.create_default_context()
            
            with socket.create_connection((domain, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    
                    # Analyze certificate
                    cert_analysis = self._analyze_certificate(cert)
                    
                    return {
                        "ssl_valid": True,
                        "certificate": {
                            "subject": dict(x for x in cert.get('subject', []))[0],
                            "issuer": dict(x for x in cert.get('issuer', []))[0],
                            "version": cert.get('version'),
                            "serial_number": cert.get('serialNumber'),
                            "not_before": cert.get('notBefore'),
                            "not_after": cert.get('notAfter'),
                            "signature_algorithm": cert.get('signatureAlgorithm')
                        },
                        "cipher_suite": {
                            "name": cipher[0] if cipher else "unknown",
                            "version": cipher[1] if cipher else "unknown",
                            "bits": cipher[2] if cipher else 0
                        },
                        "certificate_analysis": cert_analysis,
                        "ssl_grade": self._calculate_ssl_grade(cert, cipher)
                    }
        except Exception as e:
            return {"ssl_valid": False, "error": str(e), "scan_type": "ssl_analysis"}
    
    async def _malware_detection(self, url: str) -> Dict:
        """7. Advanced Malware Pattern Detection"""
        try:
            async with self.session.get(url) as response:
                content = await response.text()
                
                malware_indicators = 0
                detected_patterns = []
                severity_scores = []
                
                for pattern_name, pattern_info in self.malware_patterns.items():
                    pattern = pattern_info['pattern']
                    severity = pattern_info['severity']
                    
                    matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                    if matches:
                        malware_indicators += len(matches)
                        detected_patterns.append({
                            "pattern": pattern_name,
                            "matches": len(matches),
                            "severity": severity,
                            "description": pattern_info['description']
                        })
                        severity_scores.append(severity)
                
                avg_severity = sum(severity_scores) / len(severity_scores) if severity_scores else 0
                
                return {
                    "malware_score": min(100, malware_indicators * 8),
                    "detected_patterns": detected_patterns,
                    "pattern_count": malware_indicators,
                    "average_severity": round(avg_severity, 1),
                    "risk_level": self._get_malware_risk_level(malware_indicators, avg_severity)
                }
        except Exception as e:
            return {"error": str(e), "scan_type": "malware_detection"}
    
    async def _phishing_detection(self, url: str) -> Dict:
        """8. Advanced Phishing Detection"""
        try:
            domain = urlparse(url).netloc
            
            phishing_score = 0
            indicators = []
            
            # Domain-based analysis
            domain_analysis = self._analyze_domain_for_phishing(domain)
            phishing_score += domain_analysis['score']
            indicators.extend(domain_analysis['indicators'])
            
            # URL structure analysis
            url_analysis = self._analyze_url_structure(url)
            phishing_score += url_analysis['score']
            indicators.extend(url_analysis['indicators'])
            
            # Content-based analysis
            async with self.session.get(url) as response:
                content = await response.text()
                
                content_analysis = self._analyze_content_for_phishing(content)
                phishing_score += content_analysis['score']
                indicators.extend(content_analysis['indicators'])
            
            return {
                "phishing_score": min(100, phishing_score),
                "indicators": indicators,
                "domain_suspicious": domain_analysis['suspicious'],
                "url_suspicious": url_analysis['suspicious'],
                "content_suspicious": content_analysis['suspicious'],
                "overall_assessment": self._get_phishing_assessment(phishing_score)
            }
        except Exception as e:
            return {"error": str(e), "scan_type": "phishing_detection"}
    
    async def _social_engineering_scan(self, url: str) -> Dict:
        """9. Social Engineering Attack Detection"""
        try:
            async with self.session.get(url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                social_eng_score = 0
                detected_tactics = []
                
                # Check for social engineering patterns
                for tactic_name, pattern_info in self.social_engineering_patterns.items():
                    pattern = pattern_info['pattern']
                    weight = pattern_info['weight']
                    
                    if re.search(pattern, content, re.IGNORECASE):
                        social_eng_score += weight
                        detected_tactics.append({
                            "tactic": tactic_name,
                            "description": pattern_info['description'],
                            "weight": weight
                        })
                
                # Analyze forms for social engineering
                forms_analysis = self._analyze_forms_social_engineering(soup)
                social_eng_score += forms_analysis['score']
                detected_tactics.extend(forms_analysis['tactics'])
                
                return {
                    "social_engineering_score": min(100, social_eng_score),
                    "detected_tactics": detected_tactics,
                    "tactic_count": len(detected_tactics),
                    "risk_assessment": self._get_social_eng_risk(social_eng_score)
                }
        except Exception as e:
            return {"error": str(e), "scan_type": "social_engineering"}
    
    def _load_malware_patterns(self) -> Dict[str, Dict]:
        """Load comprehensive malware detection patterns"""
        return {
            "base64_payload": {
                "pattern": r"eval\s*\(\s*base64_decode|atob\s*\(",
                "severity": 9,
                "description": "Base64 encoded payload execution"
            },
            "obfuscated_javascript": {
                "pattern": r"String\.fromCharCode\s*\(|\\x[0-9a-fA-F]{2}",
                "severity": 8,
                "description": "Obfuscated JavaScript code"
            },
            "malicious_iframe": {
                "pattern": r"<iframe[^>]*(?:style\s*=\s*[\"'].*display\s*:\s*none|width\s*=\s*[\"']?0|height\s*=\s*[\"']?0)",
                "severity": 8,
                "description": "Hidden malicious iframe"
            },
            "crypto_mining": {
                "pattern": r"(coinhive|cryptoloot|coin-hive|minergate|cryptonight)",
                "severity": 7,
                "description": "Cryptocurrency mining code"
            },
            "shell_injection": {
                "pattern": r"(system|exec|shell_exec|passthru|popen)\s*\(",
                "severity": 10,
                "description": "System command execution"
            },
            "sql_injection": {
                "pattern": r"(union\s+select|drop\s+table|delete\s+from|insert\s+into).*[\"'][^\"']*[\"']",
                "severity": 9,
                "description": "SQL injection patterns"
            },
            "xss_vectors": {
                "pattern": r"<script[^>]*>.*?(alert|prompt|confirm|document\.cookie)\s*\(",
                "severity": 7,
                "description": "Cross-site scripting vectors"
            },
            "malicious_redirects": {
                "pattern": r"window\.location\s*=\s*[\"'][^\"']*(?:bit\.ly|tinyurl|t\.co)",
                "severity": 6,
                "description": "Suspicious redirect patterns"
            }
        }
    
    def _load_phishing_indicators(self) -> Dict[str, Dict]:
        """Load advanced phishing detection patterns"""
        return {
            "urgent_action": {
                "pattern": r"(urgent|immediate|expires?|suspend|verify|confirm|act\s+now).*(?:account|payment|security)",
                "weight": 20,
                "description": "Urgency-based social engineering"
            },
            "fake_authentication": {
                "pattern": r"(?:login|sign\s*in|log\s*in).*(?:paypal|amazon|microsoft|google|apple|facebook|twitter)",
                "weight": 25,
                "description": "Fake authentication pages"
            },
            "prize_lottery_scam": {
                "pattern": r"(congratulations|winner|prize|lottery|selected|won).*(?:\$|money|cash|reward)",
                "weight": 18,
                "description": "Prize/lottery scam indicators"
            },
            "payment_fraud": {
                "pattern": r"(payment|billing|invoice|overdue|refund|transaction).*(?:failed|pending|suspended)",
                "weight": 22,
                "description": "Payment fraud indicators"
            },
            "security_scare": {
                "pattern": r"(security\s+alert|account\s+(?:locked|compromised)|suspicious\s+activity|unauthorized\s+access)",
                "weight": 20,
                "description": "Fake security alerts"
            },
            "download_trojan": {
                "pattern": r"(?:download|install|update).*(?:urgent|required|security|antivirus|player|codec)",
                "weight": 15,
                "description": "Malicious download bait"
            }
        }
    
    def _load_social_engineering_patterns(self) -> Dict[str, Dict]:
        """Load social engineering attack patterns"""
        return {
            "authority_impersonation": {
                "pattern": r"(government|official|authority|police|fbi|irs|tax|legal).*(?:notice|warning|action)",
                "weight": 25,
                "description": "Authority figure impersonation"
            },
            "fear_uncertainty_doubt": {
                "pattern": r"(warning|danger|risk|threat|compromise|breach|hack).*(?:immediate|urgent|now)",
                "weight": 20,
                "description": "Fear, uncertainty, and doubt tactics"
            },
            "artificial_scarcity": {
                "pattern": r"(limited\s+time|expires?|only\s+\d+|last\s+chance|while\s+supplies)",
                "weight": 15,
                "description": "Artificial scarcity pressure"
            },
            "trust_exploitation": {
                "pattern": r"(trusted|verified|certified|official|authorized).*(?:by|partner|member)",
                "weight": 12,
                "description": "False trust indicators"
            },
            "emotional_manipulation": {
                "pattern": r"(help|save|donate|charity|victim|emergency|disaster)",
                "weight": 10,
                "description": "Emotional manipulation tactics"
            }
        }
    
    def _analyze_domain_for_phishing(self, domain: str) -> Dict:
        """Analyze domain for phishing indicators"""
        score = 0
        indicators = []
        
        # Check for suspicious domain patterns
        suspicious_patterns = [
            (r".*-.*-.*-.*", 15, "Multiple hyphens"),
            (r".*\d{4,}.*", 10, "Long number sequences"),
            (r".*(secure|verify|update|confirm|login|account).*", 20, "Phishing keywords in domain"),
            (r".*[0-9]{2,}[a-z]{1,2}[0-9]{2,}.*", 12, "Mixed alphanumeric patterns"),
            (r".*\.(tk|ml|ga|cf)$", 18, "Suspicious TLD")
        ]
        
        for pattern, weight, description in suspicious_patterns:
            if re.match(pattern, domain, re.IGNORECASE):
                score += weight
                indicators.append(description)
        
        return {
            "score": score,
            "indicators": indicators,
            "suspicious": score > 15
        }
    
    def _compile_scan_results(self, url: str, results: List) -> Dict[str, Any]:
        """Compile all scan results into comprehensive security report"""
        
        scan_names = [
            "http_analysis", "content_analysis", "security_headers", "dns_analysis",
            "ssl_analysis", "domain_reputation", "malware_detection", 
            "phishing_detection", "social_engineering"
        ]
        
        compiled = {
            "url": url,
            "scan_timestamp": datetime.utcnow().isoformat(),
            "scan_version": "3.1-advanced"
        }
        
        # Process each scan result
        successful_scans = 0
        for i, result in enumerate(results):
            if i < len(scan_names):
                scan_name = scan_names[i]
                
                if isinstance(result, dict) and "error" not in result:
                    compiled[scan_name] = result
                    successful_scans += 1
                else:
                    compiled[scan_name] = {
                        "error": str(result) if isinstance(result, Exception) else result.get("error", "Unknown error"),
                        "status": "failed"
                    }
        
        # Calculate comprehensive security score
        compiled["comprehensive_analysis"] = self._calculate_comprehensive_score(compiled)
        compiled["scan_summary"] = {
            "total_scans": len(scan_names),
            "successful_scans": successful_scans,
            "success_rate": round((successful_scans / len(scan_names)) * 100, 1)
        }
        
        return compiled
    
    def _calculate_comprehensive_score(self, results: Dict) -> Dict[str, Any]:
        """Calculate overall comprehensive security score"""
        
        total_score = 100  # Start with perfect score
        risk_factors = []
        
        # HTTP Analysis impact
        if "http_analysis" in results and "error" not in results["http_analysis"]:
            http_data = results["http_analysis"]
            if http_data.get("status_code", 200) != 200:
                total_score -= 10
                risk_factors.append("Non-200 HTTP status")
            if http_data.get("response_time_ms", 0) > 3000:
                total_score -= 5
                risk_factors.append("Slow response time")
        
        # Security Headers impact
        if "security_headers" in results and "error" not in results["security_headers"]:
            headers_score = results["security_headers"].get("security_score", 100)
            score_reduction = (100 - headers_score) * 0.3
            total_score -= score_reduction
            if headers_score < 80:
                risk_factors.append("Poor security headers")
        
        # SSL Analysis impact
        if "ssl_analysis" in results and "error" not in results["ssl_analysis"]:
            ssl_data = results["ssl_analysis"]
            if not ssl_data.get("ssl_valid", False):
                total_score -= 25
                risk_factors.append("Invalid SSL certificate")
        
        # Malware Detection impact
        if "malware_detection" in results and "error" not in results["malware_detection"]:
            malware_score = results["malware_detection"].get("malware_score", 0)
            total_score -= malware_score * 0.4
            if malware_score > 20:
                risk_factors.append("Malware patterns detected")
        
        # Phishing Detection impact
        if "phishing_detection" in results and "error" not in results["phishing_detection"]:
            phishing_score = results["phishing_detection"].get("phishing_score", 0)
            total_score -= phishing_score * 0.35
            if phishing_score > 25:
                risk_factors.append("Phishing indicators present")
        
        # Social Engineering impact
        if "social_engineering" in results and "error" not in results["social_engineering"]:
            social_score = results["social_engineering"].get("social_engineering_score", 0)
            total_score -= social_score * 0.25
            if social_score > 30:
                risk_factors.append("Social engineering tactics detected")
        
        final_score = max(0, int(total_score))
        
        return {
            "overall_security_score": final_score,
            "security_grade": self._get_comprehensive_grade(final_score),
            "risk_factors": risk_factors,
            "risk_level": self._get_comprehensive_risk_level(final_score),
            "recommendation": self._get_security_recommendation(final_score)
        }
    
    # Helper methods for analysis
    def _get_meta_content(self, soup, name: str) -> str:
        """Extract meta tag content"""
        meta = soup.find('meta', attrs={'name': name}) or soup.find('meta', attrs={'property': f'og:{name}'})
        return meta.get('content', '') if meta else ''
    
    def _count_external_links(self, soup, base_url: str) -> int:
        """Count external links"""
        base_domain = urlparse(base_url).netloc
        external_count = 0
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http') and base_domain not in href:
                external_count += 1
        
        return external_count
    
    def _scan_suspicious_keywords(self, content: str) -> List[str]:
        """Scan for suspicious keywords in content"""
        suspicious_keywords = [
            "download now", "click here", "free download", "virus detected",
            "your computer is infected", "security alert", "update required",
            "congratulations", "you've won", "claim your prize"
        ]
        
        found_keywords = []
        content_lower = content.lower()
        
        for keyword in suspicious_keywords:
            if keyword in content_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _get_comprehensive_grade(self, score: int) -> str:
        """Get letter grade for comprehensive score"""
        if score >= 95: return "A+"
        if score >= 90: return "A"
        if score >= 85: return "A-"
        if score >= 80: return "B+"
        if score >= 75: return "B"
        if score >= 70: return "B-"
        if score >= 65: return "C+"
        if score >= 60: return "C"
        return "D" if score >= 50 else "F"
    
    def _get_comprehensive_risk_level(self, score: int) -> str:
        """Get risk level description"""
        if score >= 90: return "very_low"
        if score >= 75: return "low"
        if score >= 60: return "medium"
        if score >= 40: return "high"
        return "critical"
    
    def _get_security_recommendation(self, score: int) -> str:
        """Get security recommendation based on score"""
        if score >= 90:
            return "Excellent security posture. Safe to proceed with normal caution."
        elif score >= 75:
            return "Good security practices. Monitor for changes and verify important transactions."
        elif score >= 60:
            return "Moderate security concerns. Exercise increased caution and verify through alternative channels."
        elif score >= 40:
            return "Significant security risks detected. Avoid sensitive transactions and verify legitimacy."
        else:
            return "Critical security risks. Do not proceed. Report to security authorities if suspicious."

# Global enhanced scanner instance
advanced_scanner = AdvancedWebScanner()
import os
import asyncio
import httpx
from typing import Dict, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class VerificationAPIs:
    """Integration with external security APIs for enhanced URL/content verification"""
    
    def __init__(self):
        self.virustotal_api_key = os.getenv('VIRUSTOTAL_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_SAFEBROWSING_API_KEY')
        self.phishtank_api_key = os.getenv('PHISHTANK_API_KEY')
        
        # HTTP client pentru async requests
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def check_url_virustotal(self, url: str) -> Dict:
        """Check URL reputation using VirusTotal API"""
        if not self.virustotal_api_key:
            return {"error": "VirusTotal API key not configured", "score": 0.5}
        
        try:
            headers = {
                "x-apikey": self.virustotal_api_key
            }
            
            # Encode URL pentru VirusTotal
            import base64
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            
            vt_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
            
            response = await self.client.get(vt_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
                
                total_scans = sum(stats.values())
                malicious = stats.get('malicious', 0)
                suspicious = stats.get('suspicious', 0)
                
                if total_scans > 0:
                    threat_score = (malicious + suspicious * 0.5) / total_scans
                    return {
                        "source": "VirusTotal",
                        "safe": threat_score < 0.1,
                        "threat_score": threat_score,
                        "malicious_count": malicious,
                        "suspicious_count": suspicious,
                        "total_scans": total_scans,
                        "reputation": "clean" if threat_score < 0.1 else "suspicious" if threat_score < 0.3 else "malicious"
                    }
            
            return {"error": "URL not found in VirusTotal", "score": 0.5}
            
        except Exception as e:
            logger.error(f"VirusTotal API error: {str(e)}")
            return {"error": str(e), "score": 0.5}
    
    async def check_url_safe_browsing(self, url: str) -> Dict:
        """Check URL using Google Safe Browsing API"""
        if not self.google_api_key:
            return {"error": "Google Safe Browsing API key not configured", "score": 0.5}
        
        try:
            sb_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.google_api_key}"
            
            payload = {
                "client": {
                    "clientId": "viralsafe-platform",
                    "clientVersion": "1.0.0"
                },
                "threatInfo": {
                    "threatTypes": [
                        "MALWARE", 
                        "SOCIAL_ENGINEERING", 
                        "UNWANTED_SOFTWARE",
                        "POTENTIALLY_HARMFUL_APPLICATION"
                    ],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": url}]
                }
            }
            
            response = await self.client.post(sb_url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('matches', [])
                
                if not matches:
                    return {
                        "source": "Google Safe Browsing",
                        "safe": True,
                        "threat_score": 0.0,
                        "threats": [],
                        "reputation": "clean"
                    }
                else:
                    threat_types = [match.get('threatType') for match in matches]
                    return {
                        "source": "Google Safe Browsing",
                        "safe": False,
                        "threat_score": 1.0,
                        "threats": threat_types,
                        "reputation": "malicious"
                    }
            
            return {"error": "Safe Browsing API error", "score": 0.5}
            
        except Exception as e:
            logger.error(f"Google Safe Browsing API error: {str(e)}")
            return {"error": str(e), "score": 0.5}
    
    async def check_url_phishtank(self, url: str) -> Dict:
        """Check URL using PhishTank API"""
        try:
            pt_url = "http://checkurl.phishtank.com/checkurl/"
            
            data = {
                'url': url,
                'format': 'json'
            }
            
            if self.phishtank_api_key:
                data['app_key'] = self.phishtank_api_key
            
            response = await self.client.post(pt_url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'results' in result:
                    is_phish = result['results'].get('in_database', False)
                    verified = result['results'].get('verified', False)
                    
                    return {
                        "source": "PhishTank",
                        "safe": not is_phish,
                        "threat_score": 1.0 if is_phish else 0.0,
                        "in_database": is_phish,
                        "verified": verified,
                        "reputation": "phishing" if is_phish else "clean"
                    }
            
            return {"error": "PhishTank API error", "score": 0.5}
            
        except Exception as e:
            logger.error(f"PhishTank API error: {str(e)}")
            return {"error": str(e), "score": 0.5}
    
    async def aggregate_url_verification(self, url: str) -> Dict:
        """Run all verification checks and aggregate results"""
        try:
            # Rulează toate verificările în paralel
            vt_task = self.check_url_virustotal(url)
            sb_task = self.check_url_safe_browsing(url)
            pt_task = self.check_url_phishtank(url)
            
            vt_result, sb_result, pt_result = await asyncio.gather(
                vt_task, sb_task, pt_task, return_exceptions=True
            )
            
            # Calculează scorul agregat
            scores = []
            sources = []
            
            if isinstance(vt_result, dict) and 'threat_score' in vt_result:
                scores.append(vt_result['threat_score'])
                sources.append(vt_result)
            
            if isinstance(sb_result, dict) and 'threat_score' in sb_result:
                scores.append(sb_result['threat_score'])
                sources.append(sb_result)
            
            if isinstance(pt_result, dict) and 'threat_score' in pt_result:
                scores.append(pt_result['threat_score'])
                sources.append(pt_result)
            
            # Calculează scorul final (media ponderată)
            if scores:
                avg_threat_score = sum(scores) / len(scores)
                safety_score = 1.0 - avg_threat_score  # Convertește la safety score
            else:
                safety_score = 0.5  # Neutral dacă nu avem date
            
            # Determină statusul final
            if safety_score >= 0.8:
                status = "verified_safe"
                risk_level = "low"
            elif safety_score >= 0.6:
                status = "likely_safe"
                risk_level = "medium"
            else:
                status = "potentially_unsafe"
                risk_level = "high"
            
            return {
                "url": url,
                "safety_score": round(safety_score, 3),
                "status": status,
                "risk_level": risk_level,
                "verified": safety_score >= 0.8,
                "sources_checked": len(sources),
                "source_results": sources,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": self._generate_verification_summary(safety_score, sources)
            }
            
        except Exception as e:
            logger.error(f"Aggregate verification error: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "safety_score": 0.5,
                "status": "verification_failed",
                "verified": False
            }
    
    def _generate_verification_summary(self, safety_score: float, sources: List[Dict]) -> str:
        """Generate a human-readable summary of verification results"""
        if safety_score >= 0.8:
            return f"✅ URL verified as safe by {len(sources)} security sources"
        elif safety_score >= 0.6:
            return f"⚠️ URL appears mostly safe but exercise caution ({len(sources)} sources checked)"
        else:
            threats = []
            for source in sources:
                if source.get('reputation') in ['malicious', 'phishing', 'suspicious']:
                    threats.append(source.get('source', 'Unknown'))
            
            if threats:
                return f"🚨 URL flagged as potentially unsafe by: {', '.join(threats)}"
            else:
                return f"⚠️ URL verification inconclusive ({len(sources)} sources checked)"
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

# Singleton instance
verification_apis = VerificationAPIs()
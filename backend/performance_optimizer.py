import asyncio
import time
import json
import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import aiohttp
from enhanced_ai_analyzer import enhanced_ai
from advanced_scanner import advanced_scanner

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """
    Ultra-fast performance optimizer with:
    - In-memory caching (Redis alternative)
    - Parallel processing
    - Smart batching
    - Result optimization
    """
    
    def __init__(self):
        # In-memory cache (production would use Redis)
        self.scan_cache = {}
        self.analysis_cache = {}
        
        # Performance settings
        self.cache_ttl = 3600  # 1 hour cache
        self.max_cache_size = 1000
        
        # Thread pool for CPU-intensive tasks
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        logger.info("⚡ Performance Optimizer initialized with in-memory caching")
    
    async def ultra_fast_scan(self, url: str, scan_options: Dict = None) -> Dict[str, Any]:
        """
        Ultra-fast comprehensive scan with intelligent caching
        Target: <500ms for cached results, <2s for new scans
        """
        
        start_time = time.time()
        
        # Generate cache key
        cache_key = self._generate_cache_key(url, scan_options or {})
        
        # Check cache first (ultra-fast path)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            cache_time = int((time.time() - start_time) * 1000)
            cached_result["performance"]["cache_hit"] = True
            cached_result["performance"]["total_time_ms"] = cache_time
            logger.info(f"⚡ Cache hit! Result returned in {cache_time}ms")
            return cached_result
        
        # Run optimized parallel analysis
        result = await self._parallel_optimized_scan(url, scan_options or {})
        
        # Cache result for future requests
        self._cache_result(cache_key, result)
        
        total_time = int((time.time() - start_time) * 1000)
        result["performance"]["cache_hit"] = False
        result["performance"]["total_time_ms"] = total_time
        
        logger.info(f"✅ Ultra-fast scan completed in {total_time}ms")
        return result
    
    async def _parallel_optimized_scan(self, url: str, options: Dict) -> Dict[str, Any]:
        """
        Optimized parallel scanning with intelligent task prioritization
        """
        
        # Priority-based task execution
        high_priority_tasks = [
            self._quick_http_check(url),           # Fastest check
            self._ai_analysis_optimized(url),      # AI analysis
        ]
        
        medium_priority_tasks = [
            self._security_headers_quick(url),     # Headers check
            self._content_analysis_lite(url),      # Light content scan
        ]
        
        low_priority_tasks = [
            self._comprehensive_deep_scan(url),    # Full technical scan
        ] if options.get('deep_scan', True) else []
        
        # Execute in priority order with timeouts
        results = {}
        
        # High priority (must complete quickly)
        logger.info("🚀 Executing high-priority scans")
        high_results = await asyncio.gather(*high_priority_tasks, return_exceptions=True)
        results.update(self._process_priority_results(high_results, ["http_quick", "ai_analysis"]))
        
        # Medium priority (reasonable timeout)
        logger.info("📄 Executing medium-priority scans")
        medium_results = await asyncio.wait_for(
            asyncio.gather(*medium_priority_tasks, return_exceptions=True),
            timeout=3.0  # 3 second timeout
        )
        results.update(self._process_priority_results(medium_results, ["security_headers", "content_lite"]))
        
        # Low priority (optional deep scan)
        if low_priority_tasks:
            try:
                logger.info("🔍 Executing deep scan analysis")
                deep_results = await asyncio.wait_for(
                    asyncio.gather(*low_priority_tasks, return_exceptions=True),
                    timeout=5.0  # 5 second timeout
                )
                results.update(self._process_priority_results(deep_results, ["deep_scan"]))
            except asyncio.TimeoutError:
                logger.warning("⏰ Deep scan timed out, using quick results")
                results["deep_scan"] = {"status": "timeout", "message": "Deep scan exceeded time limit"}
        
        # Compile optimized results
        return self._compile_optimized_results(url, results)
    
    async def _quick_http_check(self, url: str) -> Dict:
        """Ultra-fast HTTP status and basic info"""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                async with session.head(url, allow_redirects=True) as response:
                    response_time = int((time.time() - start_time) * 1000)
                    
                    return {
                        "status_code": response.status,
                        "response_time_ms": response_time,
                        "server": response.headers.get('server', 'unknown'),
                        "content_type": response.headers.get('content-type', ''),
                        "redirects": len(response.history),
                        "ssl_enabled": url.startswith('https'),
                        "quick_assessment": "healthy" if response.status == 200 else "issues_detected"
                    }
        except Exception as e:
            return {"error": str(e), "quick_assessment": "connection_failed"}
    
    async def _ai_analysis_optimized(self, url: str) -> Dict:
        """Optimized AI analysis with caching"""
        try:
            # Quick content fetch for AI
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
                async with session.get(url) as response:
                    content = await response.text()
                    content_sample = content[:1500]  # Optimal size for AI
            
            # Run AI analysis (uses ensemble if multiple providers available)
            ai_result = await enhanced_ai.multi_ai_analysis(url, content_sample)
            
            return {
                "ai_threat_score": ai_result.get("threat_score", 50),
                "ai_confidence": ai_result.get("confidence", 85),
                "ai_insights": ai_result.get("insights", "Analysis completed"),
                "providers_used": ai_result.get("providers_used", 1),
                "ensemble": ai_result.get("ensemble", False)
            }
        except Exception as e:
            return {"error": str(e), "ai_threat_score": 50}
    
    async def _security_headers_quick(self, url: str) -> Dict:
        """Quick security headers assessment"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                async with session.get(url) as response:
                    headers = dict(response.headers)
                    
                    # Quick security score
                    security_headers = [
                        'Strict-Transport-Security',
                        'Content-Security-Policy',
                        'X-Frame-Options',
                        'X-Content-Type-Options'
                    ]
                    
                    present_headers = sum(1 for h in security_headers if h in headers)
                    security_score = (present_headers / len(security_headers)) * 100
                    
                    return {
                        "security_score": int(security_score),
                        "headers_present": present_headers,
                        "total_headers_checked": len(security_headers),
                        "has_hsts": 'Strict-Transport-Security' in headers,
                        "has_csp": 'Content-Security-Policy' in headers
                    }
        except Exception as e:
            return {"error": str(e), "security_score": 0}
    
    async def _content_analysis_lite(self, url: str) -> Dict:
        """Lightweight content analysis for performance"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
                async with session.get(url) as response:
                    content = await response.text()
                    
                    # Quick content metrics
                    return {
                        "content_size": len(content),
                        "has_forms": "<form" in content.lower(),
                        "has_scripts": "<script" in content.lower(),
                        "has_iframes": "<iframe" in content.lower(),
                        "suspicious_keywords_count": len(self._quick_keyword_scan(content)),
                        "content_analysis": "completed"
                    }
        except Exception as e:
            return {"error": str(e)}
    
    async def _comprehensive_deep_scan(self, url: str) -> Dict:
        """Full comprehensive scan (optional, for deep analysis)"""
        try:
            # Run full advanced scanner
            deep_results = await advanced_scanner.comprehensive_scan(url)
            return {
                "deep_scan_completed": True,
                "comprehensive_results": deep_results,
                "scan_depth": "maximum"
            }
        except Exception as e:
            return {"error": str(e), "deep_scan_completed": False}
    
    def _generate_cache_key(self, url: str, options: Dict) -> str:
        """Generate cache key from URL and options"""
        key_data = f"{url}:{json.dumps(options, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached result if still valid"""
        if cache_key not in self.scan_cache:
            return None
        
        cached = self.scan_cache[cache_key]
        
        # Check if cache is still valid
        if time.time() - cached["timestamp"] > self.cache_ttl:
            # Remove expired cache
            del self.scan_cache[cache_key]
            return None
        
        return cached["result"]
    
    def _cache_result(self, cache_key: str, result: Dict):
        """Cache scan result with timestamp"""
        
        # Implement simple cache size management
        if len(self.scan_cache) >= self.max_cache_size:
            # Remove oldest entries
            sorted_cache = sorted(self.scan_cache.items(), key=lambda x: x[1]["timestamp"])
            for old_key, _ in sorted_cache[:100]:  # Remove oldest 100 entries
                del self.scan_cache[old_key]
        
        self.scan_cache[cache_key] = {
            "result": result,
            "timestamp": time.time()
        }
        
        logger.info(f"📄 Result cached. Cache size: {len(self.scan_cache)}")
    
    def _process_priority_results(self, results: List, names: List[str]) -> Dict:
        """Process results from priority task execution"""
        processed = {}
        
        for i, result in enumerate(results):
            if i < len(names):
                name = names[i]
                if isinstance(result, dict) and "error" not in result:
                    processed[name] = result
                else:
                    processed[name] = {
                        "error": str(result) if isinstance(result, Exception) else str(result),
                        "status": "failed"
                    }
        
        return processed
    
    def _compile_optimized_results(self, url: str, scan_results: Dict) -> Dict[str, Any]:
        """Compile all scan results into optimized comprehensive report"""
        
        # Calculate composite scores
        composite_score = self._calculate_composite_score(scan_results)
        
        # Performance metrics
        performance_metrics = self._calculate_performance_metrics(scan_results)
        
        # Smart recommendations
        recommendations = self._generate_smart_recommendations(scan_results, composite_score)
        
        return {
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
            "scan_version": "3.1-optimized",
            "scan_type": "ultra_comprehensive",
            
            # Core results
            "composite_score": composite_score,
            "scan_results": scan_results,
            "performance": performance_metrics,
            "recommendations": recommendations,
            
            # Summary metrics
            "summary": {
                "overall_risk_level": self._get_risk_level(composite_score["final_score"]),
                "security_grade": self._get_security_grade(composite_score["final_score"]),
                "trust_rating": composite_score["trust_rating"],
                "scan_quality": performance_metrics["scan_quality"]
            }
        }
    
    def _calculate_composite_score(self, scan_results: Dict) -> Dict[str, Any]:
        """Calculate intelligent composite security score"""
        
        base_score = 85  # Start with good baseline
        confidence = 100
        risk_factors = []
        
        # HTTP Analysis impact
        if "http_quick" in scan_results:
            http_data = scan_results["http_quick"]
            if "error" not in http_data:
                if http_data.get("status_code") == 200:
                    base_score += 5
                elif http_data.get("status_code", 0) >= 400:
                    base_score -= 15
                    risk_factors.append("HTTP errors detected")
                
                # Response time impact
                response_time = http_data.get("response_time_ms", 1000)
                if response_time > 3000:
                    base_score -= 5
                    risk_factors.append("Slow response time")
            else:
                base_score -= 20
                confidence -= 15
                risk_factors.append("HTTP connection failed")
        
        # AI Analysis impact (high weight)
        if "ai_analysis" in scan_results:
            ai_data = scan_results["ai_analysis"]
            if "error" not in ai_data:
                ai_threat = ai_data.get("ai_threat_score", 50)
                ai_confidence = ai_data.get("ai_confidence", 85)
                
                # AI threat impact (inverted - lower AI threat = higher security)
                security_boost = (100 - ai_threat) * 0.3
                base_score = base_score * 0.7 + security_boost
                
                # Confidence from AI
                confidence = (confidence + ai_confidence) / 2
                
                if ai_threat > 70:
                    risk_factors.append("AI detected high threat level")
                elif ai_threat < 30:
                    risk_factors.append("AI confirms low threat level")
            else:
                confidence -= 10
        
        # Security Headers impact
        if "security_headers" in scan_results:
            headers_data = scan_results["security_headers"]
            if "error" not in headers_data:
                headers_score = headers_data.get("security_score", 50)
                base_score += (headers_score - 50) * 0.2
                
                if headers_score < 60:
                    risk_factors.append("Poor security headers configuration")
            else:
                base_score -= 5
        
        # Content Analysis impact
        if "content_lite" in scan_results:
            content_data = scan_results["content_lite"]
            if "error" not in content_data:
                if content_data.get("suspicious_keywords_count", 0) > 3:
                    base_score -= 15
                    risk_factors.append("Multiple suspicious keywords detected")
                
                if content_data.get("has_iframes", False):
                    base_score -= 5
                    risk_factors.append("Contains iframes (potential risk)")
        
        # Deep scan bonus (if available)
        if "deep_scan" in scan_results:
            deep_data = scan_results["deep_scan"]
            if deep_data.get("deep_scan_completed", False):
                confidence += 10  # Bonus confidence for deep analysis
        
        # Final score normalization
        final_score = max(0, min(100, int(base_score)))
        final_confidence = max(60, min(99, int(confidence)))
        
        # Trust rating calculation
        trust_rating = self._calculate_trust_rating(final_score, final_confidence)
        
        return {
            "final_score": final_score,
            "confidence": final_confidence,
            "trust_rating": trust_rating,
            "risk_factors": risk_factors,
            "calculation_method": "weighted_composite_scoring"
        }
    
    def _calculate_performance_metrics(self, scan_results: Dict) -> Dict:
        """Calculate performance and quality metrics"""
        
        successful_scans = len([k for k, v in scan_results.items() if isinstance(v, dict) and "error" not in v])
        total_scans = len(scan_results)
        
        # Quality assessment
        quality_score = (successful_scans / total_scans) * 100 if total_scans > 0 else 0
        
        return {
            "successful_scans": successful_scans,
            "total_scans": total_scans,
            "success_rate": round(quality_score, 1),
            "scan_quality": self._get_quality_grade(quality_score),
            "optimization_level": "ultra_fast",
            "caching_enabled": True
        }
    
    def _generate_smart_recommendations(self, scan_results: Dict, composite_score: Dict) -> List[str]:
        """Generate intelligent security recommendations"""
        
        recommendations = []
        final_score = composite_score["final_score"]
        
        # Score-based recommendations
        if final_score >= 90:
            recommendations.extend([
                "✅ Excellent security posture detected",
                "📈 Maintain current security practices",
                "🔄 Schedule periodic security reviews"
            ])
        elif final_score >= 75:
            recommendations.extend([
                "⚡ Good security foundation",
                "🔧 Consider security header improvements",
                "📉 Monitor for security updates"
            ])
        elif final_score >= 60:
            recommendations.extend([
                "⚠️ Security improvements needed",
                "🔒 Implement additional security measures",
                "🔍 Conduct detailed security audit"
            ])
        else:
            recommendations.extend([
                "🚨 Critical security issues detected",
                "❌ Immediate security remediation required",
                "📢 Consider professional security assessment"
            ])
        
        # Specific technical recommendations
        if "security_headers" in scan_results:
            headers_data = scan_results["security_headers"]
            if "error" not in headers_data and headers_data.get("security_score", 100) < 80:
                if not headers_data.get("has_hsts", False):
                    recommendations.append("🔒 Enable HTTPS Strict Transport Security (HSTS)")
                if not headers_data.get("has_csp", False):
                    recommendations.append("🛡️ Implement Content Security Policy (CSP)")
        
        # AI-based recommendations
        if "ai_analysis" in scan_results:
            ai_data = scan_results["ai_analysis"]
            if "error" not in ai_data and ai_data.get("ai_threat_score", 0) > 60:
                recommendations.append("🤖 AI detected potential security concerns - manual review advised")
        
        return recommendations[:6]  # Limit to top 6 recommendations
    
    def _quick_keyword_scan(self, content: str) -> List[str]:
        """Quick scan for suspicious keywords"""
        keywords = [
            "download now", "click here", "free download", "virus detected",
            "security alert", "update required", "congratulations", "you've won"
        ]
        
        content_lower = content.lower()
        return [kw for kw in keywords if kw in content_lower]
    
    def _calculate_trust_rating(self, score: int, confidence: int) -> str:
        """Calculate trust rating from score and confidence"""
        
        # Composite trust calculation
        trust_value = (score * 0.7) + (confidence * 0.3)
        
        if trust_value >= 95:
            return "FORTRESS" # 🛡️ Ultra-secure
        elif trust_value >= 85:
            return "SECURE"   # ✅ Highly trusted
        elif trust_value >= 70:
            return "CAUTION"  # ⚠️ Needs review
        elif trust_value >= 50:
            return "RISK"     # 🟡 Moderate risk
        else:
            return "DANGER"   # 🚨 High risk
    
    def _get_risk_level(self, score: int) -> str:
        """Get risk level description"""
        if score >= 90: return "very_low"
        if score >= 75: return "low"
        if score >= 60: return "medium"
        if score >= 40: return "high"
        return "critical"
    
    def _get_security_grade(self, score: int) -> str:
        """Get security grade"""
        if score >= 95: return "A+"
        if score >= 90: return "A"
        if score >= 85: return "A-"
        if score >= 80: return "B+"
        if score >= 75: return "B"
        if score >= 70: return "B-"
        if score >= 65: return "C+"
        return "C" if score >= 60 else "D" if score >= 50 else "F"
    
    def _get_quality_grade(self, quality: float) -> str:
        """Get scan quality grade"""
        if quality >= 95: return "Excellent"
        if quality >= 85: return "Very Good"
        if quality >= 75: return "Good"
        if quality >= 65: return "Fair"
        return "Poor"

    async def batch_scan_urls(self, urls: List[str], max_concurrent: int = 5) -> Dict:
        """Batch scan multiple URLs with controlled concurrency"""
        
        start_time = time.time()
        logger.info(f"🚀 Starting batch scan for {len(urls)} URLs")
        
        # Create semaphore to limit concurrent scans
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scan_with_semaphore(url):
            async with semaphore:
                return await self.ultra_fast_scan(url)
        
        # Run batch scan
        tasks = [scan_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile batch results
        batch_time = int((time.time() - start_time) * 1000)
        
        successful_results = [r for r in results if isinstance(r, dict)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        return {
            "batch_scan_results": {
                "total_urls": len(urls),
                "successful": len(successful_results),
                "failed": len(failed_results),
                "success_rate": round((len(successful_results) / len(urls)) * 100, 1),
                "total_time_ms": batch_time,
                "average_time_per_url": round(batch_time / len(urls), 1)
            },
            "individual_results": dict(zip(urls, results))
        }

# Global performance optimizer
performance_optimizer = PerformanceOptimizer()
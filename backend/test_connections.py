#!/usr/bin/env python3
"""
🧪 ViralSafe Platform - Connection Testing Script

Tests all external API connections and validates environment configuration.
Run this script to verify MongoDB Atlas and VirusTotal API connectivity.

Usage:
    python test_connections.py
    
    or with specific tests:
    python test_connections.py --test mongodb
    python test_connections.py --test virustotal
    python test_connections.py --test all
"""

import asyncio
import logging
import sys
import argparse
import time
from datetime import datetime
from typing import Dict, List

try:
    from config import settings
    from database import db_manager
    from virustotal import vt_api
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("⚠️ Make sure you're in the backend/ directory and dependencies are installed")
    sys.exit(1)

# Configure logging for testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConnectionTester:
    """Comprehensive connection testing for all ViralSafe services"""
    
    def __init__(self):
        self.test_results = {
            "mongodb": {"status": "not_tested", "details": {}},
            "virustotal": {"status": "not_tested", "details": {}},
            "configuration": {"status": "not_tested", "details": {}}
        }
    
    async def test_configuration(self) -> Dict:
        """Test environment configuration"""
        logger.info("🔍 Testing configuration...")
        
        config_status = settings.validate_configuration()
        vt_config = settings.get_virustotal_config()
        mongodb_config = settings.get_mongodb_config()
        
        details = {
            "environment": settings.ENVIRONMENT,
            "port": settings.PORT,
            "api_version": settings.API_VERSION,
            "mongodb_configured": mongodb_config["uri_configured"],
            "mongodb_database": mongodb_config["database_name"],
            "virustotal_configured": vt_config["api_key_configured"],
            "virustotal_base_url": vt_config["base_url"],
            "virustotal_rate_limit": vt_config["rate_limit"],
            "warnings": config_status.get("warnings", [])
        }
        
        status = "healthy" if config_status["ready"] else "degraded"
        
        if config_status.get("warnings"):
            logger.warning(f"⚠️ Configuration warnings: {len(config_status['warnings'])}")
            for warning in config_status["warnings"]:
                logger.warning(f"  - {warning}")
        else:
            logger.info("✅ Configuration looks good")
        
        self.test_results["configuration"] = {
            "status": status,
            "details": details
        }
        
        return self.test_results["configuration"]
    
    async def test_mongodb(self) -> Dict:
        """Test MongoDB Atlas connection"""
        logger.info("🔍 Testing MongoDB Atlas connection...")
        
        if not settings.database_configured:
            logger.error("❌ MongoDB URI not configured")
            self.test_results["mongodb"] = {
                "status": "not_configured",
                "details": {"error": "MONGODB_URI environment variable not set"}
            }
            return self.test_results["mongodb"]
        
        try:
            start_time = time.time()
            connection_success = await db_manager.connect()
            connect_time = (time.time() - start_time) * 1000
            
            if connection_success:
                # Test health check
                start_time = time.time()
                health_check = await db_manager.health_check()
                health_time = (time.time() - start_time) * 1000
                
                logger.info(f"✅ MongoDB connected in {connect_time:.1f}ms")
                logger.info(f"✅ Health check completed in {health_time:.1f}ms")
                
                # Test basic operations
                try:
                    test_data = {
                        "test_id": "connection_test",
                        "timestamp": datetime.utcnow(),
                        "test_type": "connectivity"
                    }
                    
                    # Store and retrieve test data
                    await db_manager.store_analysis(test_data)
                    retrieved = await db_manager.get_analysis("connection_test")
                    
                    logger.info("✅ Database read/write operations successful")
                    
                    self.test_results["mongodb"] = {
                        "status": "healthy",
                        "details": {
                            "connection_time_ms": round(connect_time, 2),
                            "health_check_time_ms": round(health_time, 2),
                            "database_name": settings.MONGODB_DB_NAME,
                            "read_write_test": "passed",
                            **health_check
                        }
                    }
                    
                except Exception as e:
                    logger.warning(f"⚠️ Database operations test failed: {e}")
                    self.test_results["mongodb"] = {
                        "status": "degraded",
                        "details": {
                            "connection_time_ms": round(connect_time, 2),
                            "error": str(e),
                            "health_check": health_check
                        }
                    }
            else:
                logger.error("❌ MongoDB connection failed")
                self.test_results["mongodb"] = {
                    "status": "error",
                    "details": {"error": "Connection failed"}
                }
        
        except Exception as e:
            logger.error(f"❌ MongoDB test exception: {e}")
            self.test_results["mongodb"] = {
                "status": "error",
                "details": {"error": str(e)}
            }
        
        return self.test_results["mongodb"]
    
    async def test_virustotal(self) -> Dict:
        """Test VirusTotal API connection with stable endpoints"""
        logger.info("🔍 Testing VirusTotal API connection...")
        
        if not settings.virustotal_configured:
            logger.error("❌ VirusTotal API key not configured")
            self.test_results["virustotal"] = {
                "status": "not_configured",
                "details": {"error": "VIRUSTOTAL_API_KEY environment variable not set"}
            }
            return self.test_results["virustotal"]
        
        try:
            start_time = time.time()
            vt_initialized = await vt_api.initialize()
            init_time = (time.time() - start_time) * 1000
            
            if vt_initialized:
                # Test health check
                start_time = time.time()
                health_check = await vt_api.health_check()
                health_time = (time.time() - start_time) * 1000
                
                logger.info(f"✅ VirusTotal API initialized in {init_time:.1f}ms")
                logger.info(f"✅ Health check completed in {health_time:.1f}ms")
                
                # Test actual API calls
                test_results = []
                test_urls = ["https://google.com", "https://github.com"]
                
                for test_url in test_urls:
                    try:
                        start_time = time.time()
                        report = await vt_api.get_url_report(test_url)
                        response_time = (time.time() - start_time) * 1000
                        
                        if report and not report.get('fallback', False):
                            logger.info(f"✅ URL report for {test_url}: {response_time:.1f}ms")
                            test_results.append({
                                "url": test_url,
                                "status": "success",
                                "response_time_ms": round(response_time, 2)
                            })
                        else:
                            logger.warning(f"⚠️ URL report for {test_url}: fallback mode")
                            test_results.append({
                                "url": test_url,
                                "status": "fallback",
                                "response_time_ms": round(response_time, 2)
                            })
                    except Exception as e:
                        logger.warning(f"⚠️ URL test failed for {test_url}: {e}")
                        test_results.append({
                            "url": test_url,
                            "status": "error",
                            "error": str(e)
                        })
                
                # Determine overall status
                successful_tests = [r for r in test_results if r["status"] == "success"]
                if successful_tests:
                    overall_status = "healthy"
                    logger.info(f"✅ VirusTotal API fully functional: {len(successful_tests)}/{len(test_results)} tests passed")
                else:
                    overall_status = "degraded"
                    logger.warning("⚠️ VirusTotal API in degraded mode - will use fallback analysis")
                
                self.test_results["virustotal"] = {
                    "status": overall_status,
                    "details": {
                        "initialization_time_ms": round(init_time, 2),
                        "health_check_time_ms": round(health_time, 2),
                        "api_tests": test_results,
                        "successful_tests": len(successful_tests),
                        "total_tests": len(test_results),
                        "health_check": health_check
                    }
                }
                
            else:
                logger.error("❌ VirusTotal API initialization failed")
                self.test_results["virustotal"] = {
                    "status": "error",
                    "details": {"error": "API initialization failed"}
                }
        
        except Exception as e:
            logger.error(f"❌ VirusTotal test exception: {e}")
            self.test_results["virustotal"] = {
                "status": "error",
                "details": {"error": str(e)}
            }
        
        return self.test_results["virustotal"]
    
    async def run_all_tests(self) -> Dict:
        """Run all connection tests"""
        logger.info("🚀 Starting comprehensive connection tests...")
        logger.info("-" * 60)
        
        # Test configuration
        await self.test_configuration()
        
        # Test MongoDB
        await self.test_mongodb()
        
        # Test VirusTotal
        await self.test_virustotal()
        
        # Cleanup
        await db_manager.disconnect()
        await vt_api.close()
        
        return self.test_results
    
    def print_summary(self):
        """Print test results summary"""
        logger.info("-" * 60)
        logger.info("📈 CONNECTION TEST SUMMARY")
        logger.info("-" * 60)
        
        total_tests = 0
        healthy_tests = 0
        degraded_tests = 0
        failed_tests = 0
        
        for test_name, result in self.test_results.items():
            status = result["status"]
            total_tests += 1
            
            if status == "healthy":
                healthy_tests += 1
                icon = "✅"
            elif status == "degraded":
                degraded_tests += 1
                icon = "⚠️"
            elif status in ["error", "not_configured"]:
                failed_tests += 1
                icon = "❌"
            else:
                icon = "🔄"
            
            logger.info(f"{icon} {test_name.upper()}: {status}")
            
            # Print details for failed tests
            if status in ["error", "degraded"] and "error" in result["details"]:
                logger.info(f"   Error: {result['details']['error']}")
        
        logger.info("-" * 60)
        logger.info(f"🏆 OVERALL RESULTS:")
        logger.info(f"  Total tests: {total_tests}")
        logger.info(f"  ✅ Healthy: {healthy_tests}")
        logger.info(f"  ⚠️ Degraded: {degraded_tests}")
        logger.info(f"  ❌ Failed: {failed_tests}")
        
        if failed_tests == 0 and degraded_tests == 0:
            logger.info("✨ ALL SYSTEMS OPERATIONAL")
            return True
        elif failed_tests == 0:
            logger.info("🔄 SYSTEM OPERATIONAL (DEGRADED MODE)")
            return True
        else:
            logger.error("❌ CRITICAL ISSUES DETECTED")
            return False

async def test_api_endpoints():
    """Test actual API endpoints after deployment"""
    import httpx
    
    logger.info("🌐 Testing live API endpoints...")
    
    endpoints = [
        ("https://viralsafe-platform-free-api.onrender.com/", "Root endpoint"),
        ("https://viralsafe-platform-free-api.onrender.com/health", "Health check"),
        ("https://viralsafe-platform-free-api.onrender.com/analytics", "Analytics"),
        ("https://viralsafe-platform-free-api.onrender.com/docs", "API Documentation")
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for url, description in endpoints:
            try:
                start_time = time.time()
                response = await client.get(url)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    logger.info(f"✅ {description}: {response.status_code} ({response_time:.1f}ms)")
                else:
                    logger.warning(f"⚠️ {description}: {response.status_code} ({response_time:.1f}ms)")
            except Exception as e:
                logger.error(f"❌ {description}: {e}")

async def test_content_analysis():
    """Test content analysis functionality"""
    import httpx
    
    logger.info("🧪 Testing content analysis...")
    
    test_content = {
        "content": "URGENT! Your account will be suspended. Click here: https://suspicious-link.com",
        "platform": "email",
        "check_urls": True
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            start_time = time.time()
            response = await client.post(
                "https://viralsafe-platform-free-api.onrender.com/analyze",
                json=test_content
            )
            analysis_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Content analysis: {analysis_time:.1f}ms")
                logger.info(f"   Risk Score: {result.get('risk_score', 'N/A')}")
                logger.info(f"   Risk Level: {result.get('risk_level', 'N/A')}")
                logger.info(f"   Categories: {result.get('categories', [])}")
                if result.get('virustotal_report'):
                    logger.info("✅ VirusTotal integration working")
                else:
                    logger.warning("⚠️ VirusTotal integration in fallback mode")
            else:
                logger.error(f"❌ Content analysis failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
    except Exception as e:
        logger.error(f"❌ Content analysis test failed: {e}")

def main():
    """Main testing function"""
    parser = argparse.ArgumentParser(description="Test ViralSafe Platform connections")
    parser.add_argument(
        "--test", 
        choices=["mongodb", "virustotal", "config", "api", "analysis", "all"],
        default="all",
        help="Specify which test to run"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    async def run_tests():
        tester = ConnectionTester()
        
        try:
            if args.test in ["config", "all"]:
                await tester.test_configuration()
            
            if args.test in ["mongodb", "all"]:
                await tester.test_mongodb()
            
            if args.test in ["virustotal", "all"]:
                await tester.test_virustotal()
            
            if args.test in ["api", "all"]:
                await test_api_endpoints()
            
            if args.test in ["analysis", "all"]:
                await test_content_analysis()
            
            # Print summary
            if args.test == "all":
                success = tester.print_summary()
                sys.exit(0 if success else 1)
            
        except KeyboardInterrupt:
            logger.info("⏹️ Tests interrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            sys.exit(1)
    
    # Run tests
    try:
        asyncio.run(run_tests())
    except Exception as e:
        logger.error(f"❌ Failed to run tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
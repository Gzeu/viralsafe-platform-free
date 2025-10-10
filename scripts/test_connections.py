#!/usr/bin/env python3
"""
ViralSafe Platform - Connection Tests
Test MongoDB Atlas and VirusTotal API connections before deployment
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from config import settings
from database import db_manager
from virustotal import vt_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_configuration():
    """Test environment configuration"""
    print("\n🔧 Testing Configuration...")
    print("=" * 40)
    
    config_status = settings.validate_configuration()
    
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Port: {settings.PORT}")
    print(f"MongoDB configured: {'✅' if config_status['mongodb'] else '❌'}")
    print(f"VirusTotal configured: {'✅' if config_status['virustotal'] else '❌'}")
    print(f"Hash salt configured: {'✅' if settings.HASH_SALT != 'default_salt_change_in_production' else '❌'}")
    
    if not config_status['ready']:
        print("\n⚠️  Configuration incomplete!")
        if not config_status['mongodb']:
            print("   - MONGODB_URI not set")
        if not config_status['virustotal']:
            print("   - VIRUSTOTAL_API_KEY not set")
        if settings.HASH_SALT == 'default_salt_change_in_production':
            print("   - HASH_SALT not set to secure value")
    else:
        print("\n✅ Configuration complete!")
    
    return config_status['ready']

async def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    print("\n🔍 Testing MongoDB Atlas Connection...")
    print("=" * 40)
    
    try:
        # Test connection
        connected = await db_manager.connect()
        
        if connected:
            # Get health status
            health = await db_manager.health_check()
            
            print(f"✅ MongoDB Atlas: Connected successfully")
            print(f"   Database: {settings.MONGODB_DB_NAME}")
            print(f"   Response time: {health.get('response_time_ms', 0):.2f}ms")
            
            collections = health.get('collections', {})
            if collections:
                print(f"   Collections: {len(collections)}")
                for name, count in collections.items():
                    print(f"     - {name}: {count} documents")
            
            return True
        else:
            print("❌ MongoDB Atlas: Connection failed")
            print("   Check MONGODB_URI in environment variables")
            return False
            
    except Exception as e:
        print(f"❌ MongoDB Atlas: Connection error")
        print(f"   Error: {str(e)}")
        return False

async def test_virustotal_api():
    """Test VirusTotal API connection"""
    print("\n🛡️  Testing VirusTotal API Connection...")
    print("=" * 40)
    
    try:
        # Initialize API
        initialized = await vt_api.initialize()
        
        if initialized:
            # Get health status
            health = await vt_api.health_check()
            
            print(f"✅ VirusTotal API: Connected successfully")
            print(f"   Response time: {health.get('response_time_ms', 0):.2f}ms")
            print(f"   Rate limit remaining: {health.get('rate_limit_remaining', 0)}/{settings.VIRUSTOTAL_RATE_LIMIT}")
            
            # Display quota information
            quotas = health.get('quotas', {})
            if quotas and 'api_requests_daily' in quotas:
                daily = quotas['api_requests_daily']
                used = daily.get('used', 0)
                allowed = daily.get('allowed', 0)
                print(f"   Daily quota: {used}/{allowed} requests used")
            
            return True
        else:
            print("❌ VirusTotal API: Initialization failed")
            print("   Check VIRUSTOTAL_API_KEY in environment variables")
            return False
            
    except Exception as e:
        print(f"❌ VirusTotal API: Connection error")
        print(f"   Error: {str(e)}")
        return False

async def cleanup_resources():
    """Clean up test resources"""
    try:
        # Close database connection
        await db_manager.disconnect()
        
        # Close VirusTotal client
        await vt_api.close()
        
        logger.info("Test resources cleaned up")
        
    except Exception as e:
        logger.warning(f"Cleanup error: {e}")

async def main():
    """Run all connection tests"""
    print("🛡️  ViralSafe Platform - Connection Tests")
    print("=" * 50)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Port: {settings.PORT}")
    print("=" * 50)
    
    try:
        # Run all tests
        config_ok = await test_configuration()
        mongodb_ok = await test_mongodb_connection() if config_ok else False
        virustotal_ok = await test_virustotal_api() if config_ok else False
        
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        results = {
            "Configuration": "✅" if config_ok else "❌",
            "MongoDB Atlas": "✅" if mongodb_ok else "❌",
            "VirusTotal API": "✅" if virustotal_ok else "❌"
        }
        
        for test_name, status in results.items():
            print(f"{test_name:20} {status}")
        
        all_passed = all([config_ok, mongodb_ok, virustotal_ok])
        
        print("\n" + "=" * 50)
        if all_passed:
            print("🎉 ALL TESTS PASSED!")
            print("🚀 ViralSafe Platform is ready for deployment!")
            print("")
            print("Next steps:")
            print("1. Deploy to Render.com")
            print("2. Set environment variables in Render dashboard")
            print("3. Test production endpoints")
        else:
            print("⚠️  SOME TESTS FAILED")
            print("❗ Fix the issues above before deploying")
            print("")
            print("Common fixes:")
            print("- Verify GitHub Secrets are set correctly")
            print("- Check MongoDB Atlas network access")
            print("- Verify VirusTotal API key is valid")
        
        return all_passed
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        return False
    finally:
        await cleanup_resources()

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
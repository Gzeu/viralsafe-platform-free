"""
MongoDB Atlas Database Configuration and Models
Optimized for FREE tier (512MB storage, 100 operations/sec)
"""

import os
import asyncio
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """MongoDB Atlas connection manager with connection pooling"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self._connection_string = os.getenv("MONGODB_URI")
        self._db_name = os.getenv("MONGODB_DB_NAME", "viralsafe")
        self._max_pool_size = int(os.getenv("MONGODB_MAX_POOL_SIZE", "10"))
        self._min_pool_size = int(os.getenv("MONGODB_MIN_POOL_SIZE", "1"))
        
    async def connect(self):
        """Establish connection to MongoDB Atlas"""
        if not self._connection_string:
            logger.warning("MongoDB URI not configured. Using in-memory storage.")
            return False
            
        try:
            self.client = AsyncIOMotorClient(
                self._connection_string,
                maxPoolSize=self._max_pool_size,
                minPoolSize=self._min_pool_size,
                maxIdleTimeMS=30000,
                serverSelectionTimeoutMS=5000,
                socketTimeoutMS=20000,
                connectTimeoutMS=20000,
                heartbeatFrequencyMS=10000
            )
            
            # Test connection
            await self.client.admin.command('ping')
            self.database = self.client[self._db_name]
            
            # Create indexes for optimal performance
            await self._create_indexes()
            
            logger.info(f"✅ Connected to MongoDB Atlas: {self._db_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("🔌 MongoDB connection closed")
    
    async def _create_indexes(self):
        """Create database indexes for optimal query performance"""
        try:
            # Content Analyses Collection Indexes
            await self.database.content_analyses.create_indexes([
                IndexModel([("content_hash", ASCENDING)], unique=True),
                IndexModel([("timestamp", DESCENDING)]),
                IndexModel([("platform", ASCENDING)]),
                IndexModel([("risk_level", ASCENDING)]),
                IndexModel([("virustotal_scanned", ASCENDING)])
            ])
            
            # Hash Monitoring Collection Indexes
            await self.database.hash_monitoring.create_indexes([
                IndexModel([("file_hash", ASCENDING)], unique=True),
                IndexModel([("first_seen", DESCENDING)]),
                IndexModel([("threat_level", ASCENDING)]),
                IndexModel([("virustotal_positives", DESCENDING)])
            ])
            
            # VirusTotal Cache Collection Indexes
            await self.database.virustotal_cache.create_indexes([
                IndexModel([("resource_hash", ASCENDING)], unique=True),
                IndexModel([("cached_at", ASCENDING)], expireAfterSeconds=86400)  # 24h TTL
            ])
            
            # Analytics Collection Indexes
            await self.database.analytics_daily.create_indexes([
                IndexModel([("date", ASCENDING)], unique=True),
                IndexModel([("date", DESCENDING)])
            ])
            
            # API Usage Logs Indexes
            await self.database.api_usage_logs.create_indexes([
                IndexModel([("ip_address", ASCENDING), ("timestamp", DESCENDING)]),
                IndexModel([("timestamp", ASCENDING)], expireAfterSeconds=604800)  # 7 days TTL
            ])
            
            logger.info("📊 Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create indexes: {e}")

class ContentAnalysisModel:
    """Data model for content analysis results"""
    
    @staticmethod
    def create_document(
        analysis_id: str,
        content_hash: str,
        content_preview: str,
        risk_score: float,
        risk_level: str,
        categories: List[str],
        indicators: List[str],
        recommendations: List[str],
        platform: str,
        processing_time_ms: int,
        url: Optional[str] = None,
        virustotal_result: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a document for content analysis collection"""
        return {
            "analysis_id": analysis_id,
            "content_hash": content_hash,
            "content_preview": content_preview,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "categories": categories,
            "indicators": indicators,
            "recommendations": recommendations,
            "platform": platform,
            "url": url,
            "processing_time_ms": processing_time_ms,
            "virustotal_result": virustotal_result,
            "virustotal_scanned": virustotal_result is not None,
            "timestamp": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        }

class HashMonitoringModel:
    """Data model for hash monitoring and threat tracking"""
    
    @staticmethod
    def create_document(
        file_hash: str,
        hash_type: str,
        threat_level: str,
        virustotal_positives: int,
        virustotal_total: int,
        threat_names: List[str],
        first_seen_source: str
    ) -> Dict[str, Any]:
        """Create a document for hash monitoring collection"""
        return {
            "file_hash": file_hash,
            "hash_type": hash_type,  # md5, sha256, sha1
            "threat_level": threat_level,  # clean, suspicious, malicious
            "virustotal_positives": virustotal_positives,
            "virustotal_total": virustotal_total,
            "threat_names": threat_names,
            "first_seen_source": first_seen_source,
            "first_seen": datetime.now(timezone.utc),
            "last_updated": datetime.now(timezone.utc),
            "scan_count": 1,
            "sources": [first_seen_source]
        }

class VirusTotalCacheModel:
    """Data model for VirusTotal API response caching"""
    
    @staticmethod
    def create_document(
        resource_hash: str,
        resource_type: str,
        scan_result: Dict[str, Any],
        positives: int,
        total: int
    ) -> Dict[str, Any]:
        """Create a document for VirusTotal cache collection"""
        return {
            "resource_hash": resource_hash,
            "resource_type": resource_type,  # url, file, domain
            "scan_result": scan_result,
            "positives": positives,
            "total": total,
            "cached_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc)
        }

class AnalyticsModel:
    """Data model for daily analytics aggregation"""
    
    @staticmethod
    def create_daily_document(date: str) -> Dict[str, Any]:
        """Create a document for daily analytics collection"""
        return {
            "date": date,
            "total_analyses": 0,
            "risk_distribution": {"high": 0, "medium": 0, "low": 0},
            "platform_stats": {},
            "virustotal_scans": 0,
            "hash_detections": 0,
            "unique_ips": set(),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }

# Global database manager instance
db_manager = DatabaseManager()

async def get_database() -> Optional[AsyncIOMotorDatabase]:
    """Get database instance"""
    if not db_manager.database:
        await db_manager.connect()
    return db_manager.database

async def init_database():
    """Initialize database connection on startup"""
    success = await db_manager.connect()
    if not success:
        logger.warning("⚠️ Running in fallback mode without MongoDB Atlas")
    return success

async def close_database():
    """Close database connection on shutdown"""
    await db_manager.disconnect()
import asyncio
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """MongoDB Atlas database manager with connection pooling and error handling"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.connected = False
    
    async def connect(self) -> bool:
        """Initialize MongoDB Atlas connection"""
        try:
            if not settings.MONGODB_URI:
                logger.error("MongoDB URI not configured")
                return False
            
            # Create client with connection options
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000,  # 5 seconds timeout
                connectTimeoutMS=10000,         # 10 seconds connect timeout
                maxPoolSize=10,                 # Free tier limit
                minPoolSize=1,
                retryWrites=True
            )
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Get database
            self.database = self.client[settings.MONGODB_DB_NAME]
            
            # Create indexes for better performance
            await self.create_indexes()
            
            self.connected = True
            logger.info(f"Connected to MongoDB Atlas: {settings.MONGODB_DB_NAME}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected database error: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("Disconnected from MongoDB")
    
    async def create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Analyses collection indexes
            analyses = self.database.analyses
            await analyses.create_index("content_hash", unique=True)
            await analyses.create_index("timestamp")
            await analyses.create_index("risk_level")
            await analyses.create_index("platform")
            
            # User analytics collection indexes
            analytics = self.database.analytics
            await analytics.create_index("date", unique=True)
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Index creation failed (non-critical): {e}")
    
    async def health_check(self) -> dict:
        """Check database health and connection status"""
        try:
            if not self.connected or not self.client:
                return {"status": "disconnected", "error": "No active connection"}
            
            # Test with a simple ping
            start_time = asyncio.get_event_loop().time()
            await self.client.admin.command('ping')
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Get collection stats
            stats = await self.get_collection_stats()
            
            return {
                "status": "connected",
                "database": settings.MONGODB_DB_NAME,
                "response_time_ms": round(response_time, 2),
                "collections": stats
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def get_collection_stats(self) -> dict:
        """Get collection statistics"""
        try:
            collections = await self.database.list_collection_names()
            stats = {}
            
            for collection_name in collections:
                collection = self.database[collection_name]
                count = await collection.count_documents({})
                stats[collection_name] = count
            
            return stats
        except Exception:
            return {}
    
    async def store_analysis(self, analysis_data: dict) -> bool:
        """Store analysis result in database"""
        try:
            if not self.connected:
                return False
            
            # Add storage timestamp
            analysis_data['stored_at'] = datetime.utcnow()
            
            # Store in analyses collection
            result = await self.database.analyses.insert_one(analysis_data)
            
            # Update daily analytics
            await self.update_daily_analytics(analysis_data)
            
            return bool(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to store analysis: {e}")
            return False
    
    async def get_analysis(self, analysis_id: str) -> Optional[dict]:
        """Retrieve analysis by ID"""
        try:
            if not self.connected:
                return None
            
            result = await self.database.analyses.find_one({"id": analysis_id})
            return result
            
        except Exception as e:
            logger.error(f"Failed to retrieve analysis: {e}")
            return None
    
    async def get_analytics(self) -> dict:
        """Get aggregated analytics data"""
        try:
            if not self.connected:
                return self.get_default_analytics()
            
            # Aggregate data from last 30 days
            since_date = datetime.utcnow() - timedelta(days=30)
            
            pipeline = [
                {"$match": {"timestamp": {"$gte": since_date}}},
                {
                    "$group": {
                        "_id": None,
                        "total_analyses": {"$sum": 1},
                        "avg_risk_score": {"$avg": "$risk_score"},
                        "high_risk": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "high"]}, 1, 0]}
                        },
                        "medium_risk": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "medium"]}, 1, 0]}
                        },
                        "low_risk": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "low"]}, 1, 0]}
                        }
                    }
                }
            ]
            
            result = await self.database.analyses.aggregate(pipeline).to_list(1)
            
            if result:
                data = result[0]
                return {
                    "total_analyses": data.get("total_analyses", 0),
                    "avg_risk_score": round(data.get("avg_risk_score", 0), 3),
                    "risk_distribution": {
                        "high": data.get("high_risk", 0),
                        "medium": data.get("medium_risk", 0),
                        "low": data.get("low_risk", 0)
                    }
                }
            
            return self.get_default_analytics()
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return self.get_default_analytics()
    
    async def update_daily_analytics(self, analysis_data: dict):
        """Update daily analytics counters"""
        try:
            today = datetime.utcnow().date()
            
            await self.database.analytics.update_one(
                {"date": today},
                {
                    "$inc": {
                        "total_analyses": 1,
                        f"risk_levels.{analysis_data['risk_level']}": 1,
                        f"platforms.{analysis_data['platform']}": 1
                    },
                    "$setOnInsert": {"created_at": datetime.utcnow()}
                },
                upsert=True
            )
        except Exception as e:
            logger.warning(f"Failed to update daily analytics: {e}")
    
    def get_default_analytics(self) -> dict:
        """Return default analytics when database is unavailable"""
        return {
            "total_analyses": 0,
            "avg_risk_score": 0.0,
            "risk_distribution": {"high": 0, "medium": 0, "low": 0}
        }

# Global database instance
db_manager = DatabaseManager()
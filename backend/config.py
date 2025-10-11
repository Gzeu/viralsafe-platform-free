import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Settings:
    """
    Enhanced configuration management for ViralSafe v3.1
    Handles all environment variables with validation and defaults
    """
    
    def __init__(self):
        # Core API Settings
        self.API_TITLE = "ViralSafe Platform Enhanced API"
        self.API_VERSION = "3.1.0"
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.PORT = int(os.getenv("PORT", 10000))
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # AI Provider Settings (NEW in v3.1)
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        
        # Database Settings
        self.MONGODB_URI = os.getenv("MONGODB_URI")
        self.MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "viralsafe")
        self.DATABASE_PING_TIMEOUT = int(os.getenv("DATABASE_PING_TIMEOUT", 5))
        
        # Security API Settings
        self.VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
        self.VIRUSTOTAL_BASE_URL = os.getenv("VIRUSTOTAL_BASE_URL", "https://www.virustotal.com/api/v3")
        self.VIRUSTOTAL_RATE_LIMIT = int(os.getenv("VIRUSTOTAL_RATE_LIMIT", 4))
        self.VIRUSTOTAL_TIMEOUT = int(os.getenv("VIRUSTOTAL_TIMEOUT", 30))
        self.VIRUSTOTAL_MAX_RETRIES = int(os.getenv("VIRUSTOTAL_MAX_RETRIES", 3))
        
        # Security Configuration
        self.HASH_SALT = os.getenv("HASH_SALT", "default_salt_change_in_production")
        
        # Performance Settings (Enhanced for v3.1)
        self.MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 10000))
        self.MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", 10))
        self.CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 15))
        self.HEALTH_CHECK_TIMEOUT = int(os.getenv("HEALTH_CHECK_TIMEOUT", 10))
        
        # Rate Limiting
        self.RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", 100))
        self.RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))
        
        # CORS Settings
        self.ALLOWED_ORIGINS = self._get_allowed_origins()
        
        # Feature Flags (Enhanced for v3.1)
        self.database_configured = bool(self.MONGODB_URI)
        self.virustotal_configured = bool(self.VIRUSTOTAL_API_KEY)
        self.ai_configured = bool(self.GROQ_API_KEY)
        self.multi_ai_enabled = bool(self.GROQ_API_KEY and (self.ANTHROPIC_API_KEY or self.OPENAI_API_KEY))
        self.is_production = self.ENVIRONMENT.lower() == "production"
        self.is_development = self.ENVIRONMENT.lower() == "development"
        
        logger.info(f"⚙️ ViralSafe v{self.API_VERSION} configuration loaded for {self.ENVIRONMENT} environment")
        
    def _get_allowed_origins(self) -> list:
        """Get CORS allowed origins based on environment"""
        base_origins = [
            "https://viralsafe-platform-free.vercel.app",
            "https://gzeu.github.io",
            "https://viralsafe-platform-free-api.onrender.com"
        ]
        
        if not self.is_production:
            base_origins.extend([
                "http://localhost:3000",
                "http://localhost:3001", 
                "http://localhost:5173",
                "http://127.0.0.1:3000"
            ])
        
        return base_origins
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Enhanced configuration validation for v3.1"""
        validation_result = {
            "service": "ViralSafe Enhanced API",
            "version": self.API_VERSION,
            "environment": self.ENVIRONMENT,
            "port": self.PORT,
            "ready": True,  # Always ready with graceful degradation
            "services": {
                "mongodb": self.database_configured,
                "virustotal": self.virustotal_configured
            },
            "ai_providers": {
                "groq": bool(self.GROQ_API_KEY),
                "anthropic": bool(self.ANTHROPIC_API_KEY),
                "openai": bool(self.OPENAI_API_KEY),
                "total_configured": sum([
                    bool(self.GROQ_API_KEY),
                    bool(self.ANTHROPIC_API_KEY), 
                    bool(self.OPENAI_API_KEY)
                ])
            },
            "features_enabled": {
                "database_storage": self.database_configured,
                "ai_analysis": self.ai_configured,
                "multi_ai_ensemble": self.multi_ai_enabled,
                "advanced_scanning": True,
                "threat_intelligence": self.ai_configured,
                "real_time_monitoring": True,
                "batch_processing": True,
                "performance_optimization": True
            },
            "warnings": [],
            "fallback_mode": False
        }
        
        # Add warnings for missing optional configurations
        warnings = []
        if not self.database_configured:
            warnings.append("MongoDB not configured - analytics and storage disabled")
        if not self.ai_configured:
            warnings.append("AI providers not configured - using basic fallback analysis")
        if not self.virustotal_configured:
            warnings.append("VirusTotal not configured - URL scanning disabled")
        if self.HASH_SALT == "default_salt_change_in_production" and self.is_production:
            warnings.append("Default salt in production - security risk")
        if not self.multi_ai_enabled and self.ai_configured:
            warnings.append("Single AI provider configured - consider adding secondary providers for ensemble analysis")
        
        validation_result["warnings"] = warnings
        validation_result["fallback_mode"] = len(warnings) > 0
        
        return validation_result
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration (sanitized)"""
        return {
            "uri_configured": bool(self.MONGODB_URI),
            "database_name": self.MONGODB_DB_NAME,
            "ping_timeout": self.DATABASE_PING_TIMEOUT,
            "status": "configured" if self.database_configured else "not_configured"
        }
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI provider configuration (sanitized)"""
        return {
            "providers": {
                "groq": {
                    "configured": bool(self.GROQ_API_KEY),
                    "priority": 1,
                    "status": "primary" if self.GROQ_API_KEY else "not_configured"
                },
                "anthropic": {
                    "configured": bool(self.ANTHROPIC_API_KEY),
                    "priority": 2,
                    "status": "secondary" if self.ANTHROPIC_API_KEY else "not_configured"
                },
                "openai": {
                    "configured": bool(self.OPENAI_API_KEY),
                    "priority": 3,
                    "status": "tertiary" if self.OPENAI_API_KEY else "not_configured"
                }
            },
            "ensemble_enabled": self.multi_ai_enabled,
            "fallback_enabled": True,
            "total_providers": sum([
                bool(self.GROQ_API_KEY),
                bool(self.ANTHROPIC_API_KEY),
                bool(self.OPENAI_API_KEY)
            ])
        }
    
    def get_virustotal_config(self) -> Dict[str, Any]:
        """Get VirusTotal configuration (sanitized)"""
        return {
            "api_key_configured": bool(self.VIRUSTOTAL_API_KEY),
            "base_url": self.VIRUSTOTAL_BASE_URL,
            "rate_limit": self.VIRUSTOTAL_RATE_LIMIT,
            "timeout": self.VIRUSTOTAL_TIMEOUT,
            "max_retries": self.VIRUSTOTAL_MAX_RETRIES,
            "status": "configured" if self.virustotal_configured else "not_configured"
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        return {
            "max_content_length": self.MAX_CONTENT_LENGTH,
            "max_batch_size": self.MAX_BATCH_SIZE,
            "cache_ttl": self.CACHE_TTL,
            "request_timeout": self.REQUEST_TIMEOUT,
            "health_check_timeout": self.HEALTH_CHECK_TIMEOUT,
            "rate_limiting": {
                "requests_per_minute": self.RATE_LIMIT_REQUESTS,
                "window_seconds": self.RATE_LIMIT_WINDOW
            }
        }
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a specific feature is enabled"""
        feature_map = {
            "database": self.database_configured,
            "ai_analysis": self.ai_configured,
            "multi_ai": self.multi_ai_enabled,
            "virustotal": self.virustotal_configured,
            "advanced_scanning": True,
            "threat_intelligence": self.ai_configured,
            "real_time_monitoring": True,
            "batch_processing": True,
            "performance_optimization": True,
            "analytics": self.database_configured
        }
        return feature_map.get(feature, False)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            "service": self.API_TITLE,
            "version": self.API_VERSION,
            "environment": self.ENVIRONMENT,
            "port": self.PORT,
            "log_level": self.LOG_LEVEL,
            "production": self.is_production,
            "development": self.is_development,
            "cors_origins": len(self.ALLOWED_ORIGINS),
            "features": {
                "total_enabled": sum([
                    self.database_configured,
                    self.ai_configured,
                    self.virustotal_configured,
                    True,  # advanced_scanning always enabled
                    True,  # real_time_monitoring always enabled
                    True   # batch_processing always enabled
                ]),
                "ai_providers": sum([
                    bool(self.GROQ_API_KEY),
                    bool(self.ANTHROPIC_API_KEY),
                    bool(self.OPENAI_API_KEY)
                ])
            }
        }

# Global settings instance
settings = Settings()

# Enhanced validation on module load
config_validation = settings.validate_configuration()
if config_validation["warnings"]:
    for warning in config_validation["warnings"]:
        logger.warning(f"⚠️ Config Warning: {warning}")

# Log successful configuration
logger.info(f"✅ ViralSafe v{settings.API_VERSION} configuration validated successfully")
logger.info(f"🎨 Features enabled: {sum(config_validation['features_enabled'].values())}/8")
logger.info(f"🤖 AI providers configured: {config_validation['ai_providers']['total_configured']}/3")
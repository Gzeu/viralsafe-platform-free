import os
from typing import Optional

class Settings:
    """Application configuration management using environment variables"""
    
    # MongoDB Configuration
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "viralsafe")
    
    # VirusTotal API Configuration
    VIRUSTOTAL_API_KEY: str = os.getenv("VIRUSTOTAL_API_KEY", "")
    VIRUSTOTAL_BASE_URL: str = os.getenv("VIRUSTOTAL_BASE_URL", "https://www.virustotal.com/api/v3")
    VIRUSTOTAL_RATE_LIMIT: int = int(os.getenv("VIRUSTOTAL_RATE_LIMIT", "4"))  # requests per minute (free tier)
    VIRUSTOTAL_TIMEOUT: int = int(os.getenv("VIRUSTOTAL_TIMEOUT", "30"))  # seconds
    VIRUSTOTAL_MAX_RETRIES: int = int(os.getenv("VIRUSTOTAL_MAX_RETRIES", "3"))
    
    # Security Configuration
    HASH_SALT: str = os.getenv("HASH_SALT", "default_salt_change_in_production")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Application Configuration
    PORT: int = int(os.getenv("PORT", "10000"))  # Render.com default
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "ViralSafe API"
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = [
        "https://viralsafe-platform-free.vercel.app",
        "https://gzeu.github.io",
        "http://localhost:3000",
        "http://localhost:5173"
    ]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))  # requests per minute per IP
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
    
    # Content Analysis Configuration
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", "5000"))
    MAX_BATCH_SIZE: int = int(os.getenv("MAX_BATCH_SIZE", "10"))
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    
    # Health Check Configuration
    HEALTH_CHECK_TIMEOUT: int = int(os.getenv("HEALTH_CHECK_TIMEOUT", "10"))  # seconds
    DATABASE_PING_TIMEOUT: int = int(os.getenv("DATABASE_PING_TIMEOUT", "5"))  # seconds
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    @property
    def database_configured(self) -> bool:
        return bool(self.MONGODB_URI)
    
    @property
    def virustotal_configured(self) -> bool:
        return bool(self.VIRUSTOTAL_API_KEY)
    
    def validate_configuration(self) -> dict:
        """Validate critical configuration and return status"""
        status = {
            "mongodb": self.database_configured,
            "virustotal": self.virustotal_configured,
            "environment": self.ENVIRONMENT,
            "port": self.PORT,
            "ready": False
        }
        
        # Application can run with basic functionality even without MongoDB or VirusTotal
        # Only MongoDB is considered critical for full functionality
        status["ready"] = True  # Always ready, graceful degradation
        
        # Add configuration warnings
        warnings = []
        if not self.database_configured:
            warnings.append("MongoDB not configured - using in-memory storage")
        if not self.virustotal_configured:
            warnings.append("VirusTotal API not configured - URL scanning disabled")
        if self.HASH_SALT == "default_salt_change_in_production":
            warnings.append("Default salt in use - change for production")
        
        status["warnings"] = warnings
        status["fallback_mode"] = len(warnings) > 0
        
        return status
    
    def get_virustotal_config(self) -> dict:
        """Get VirusTotal configuration for logging"""
        return {
            "api_key_configured": bool(self.VIRUSTOTAL_API_KEY),
            "base_url": self.VIRUSTOTAL_BASE_URL,
            "rate_limit": self.VIRUSTOTAL_RATE_LIMIT,
            "timeout": self.VIRUSTOTAL_TIMEOUT,
            "max_retries": self.VIRUSTOTAL_MAX_RETRIES
        }
    
    def get_mongodb_config(self) -> dict:
        """Get MongoDB configuration for logging (without sensitive data)"""
        return {
            "uri_configured": bool(self.MONGODB_URI),
            "database_name": self.MONGODB_DB_NAME,
            "ping_timeout": self.DATABASE_PING_TIMEOUT
        }

# Global settings instance
settings = Settings()
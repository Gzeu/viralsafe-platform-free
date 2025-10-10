import os
from typing import Optional

class Settings:
    """Application configuration management using environment variables"""
    
    # MongoDB Configuration
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "viralsafe")
    
    # VirusTotal API Configuration
    VIRUSTOTAL_API_KEY: str = os.getenv("VIRUSTOTAL_API_KEY", "")
    VIRUSTOTAL_RATE_LIMIT: int = 4  # requests per minute (free tier)
    VIRUSTOTAL_BASE_URL: str = "https://www.virustotal.com/api/v3"
    
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
    RATE_LIMIT_REQUESTS: int = 100  # requests per minute per IP
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Content Analysis Configuration
    MAX_CONTENT_LENGTH: int = 5000
    MAX_BATCH_SIZE: int = 10
    CACHE_TTL: int = 3600  # 1 hour
    
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
        
        # Check if all critical components are configured
        status["ready"] = all([
            status["mongodb"],
            status["virustotal"],
            bool(self.HASH_SALT != "default_salt_change_in_production")
        ])
        
        return status

# Global settings instance
settings = Settings()

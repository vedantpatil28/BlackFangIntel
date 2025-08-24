"""
BlackFang Intelligence - Configuration Settings
"""

import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Application Settings
    APP_NAME: str = "BlackFang Intelligence"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8080))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Security Settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "blackfang-production-secret-2025")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", 30))
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DATABASE_POOL_MIN_SIZE: int = int(os.getenv("DATABASE_POOL_MIN_SIZE", 5))
    DATABASE_POOL_MAX_SIZE: int = int(os.getenv("DATABASE_POOL_MAX_SIZE", 20))
    DATABASE_TIMEOUT: int = int(os.getenv("DATABASE_TIMEOUT", 60))
    
    # Redis Settings (for caching and background tasks)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080", 
        "https://*.railway.app",
        "https://*.vercel.app"
    ]
    
    # External API Keys
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    GOOGLE_PLACES_API_KEY: str = os.getenv("GOOGLE_PLACES_API_KEY", "")
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    
    # Scraping Settings
    SCRAPING_TIMEOUT: int = int(os.getenv("SCRAPING_TIMEOUT", 30))
    SCRAPING_MAX_RETRIES: int = int(os.getenv("SCRAPING_MAX_RETRIES", 3))
    SCRAPING_DELAY_MIN: int = int(os.getenv("SCRAPING_DELAY_MIN", 1))
    SCRAPING_DELAY_MAX: int = int(os.getenv("SCRAPING_DELAY_MAX", 5))
    
    # Business Settings
    DEFAULT_SUBSCRIPTION_PLAN: str = "professional"
    BASIC_PLAN_COMPETITOR_LIMIT: int = 5
    PROFESSIONAL_PLAN_COMPETITOR_LIMIT: int = 15
    ENTERPRISE_PLAN_COMPETITOR_LIMIT: int = 999
    
    # Pricing (in Indian Rupees)
    BASIC_PLAN_PRICE: int = 25000
    PROFESSIONAL_PLAN_PRICE: int = 45000
    ENTERPRISE_PLAN_PRICE: int = 75000
    
    # Alert Settings
    ALERT_EMAIL_ENABLED: bool = os.getenv("ALERT_EMAIL_ENABLED", "True").lower() == "true"
    ALERT_SMS_ENABLED: bool = os.getenv("ALERT_SMS_ENABLED", "False").lower() == "true"
    ALERT_BATCH_SIZE: int = int(os.getenv("ALERT_BATCH_SIZE", 100))
    
    # Report Settings
    REPORT_GENERATION_ENABLED: bool = os.getenv("REPORT_GENERATION_ENABLED", "True").lower() == "true"
    REPORT_RETENTION_DAYS: int = int(os.getenv("REPORT_RETENTION_DAYS", 90))
    
    # Monitoring Settings
    HEALTH_CHECK_ENABLED: bool = True
    METRICS_ENABLED: bool = os.getenv("METRICS_ENABLED", "True").lower() == "true"
    
    # Email Settings
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.sendgrid.net")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "apikey")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", SENDGRID_API_KEY)
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "True").lower() == "true"
    
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@blackfangintel.com")
    FROM_NAME: str = os.getenv("FROM_NAME", "BlackFang Intelligence")
    
    # File Storage Settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "csv", "xlsx", "png", "jpg", "jpeg"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", 100))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", 60))  # seconds
    
    # Demo Account Settings
    DEMO_ACCOUNT_ENABLED: bool = os.getenv("DEMO_ACCOUNT_ENABLED", "True").lower() == "true"
    DEMO_EMAIL: str = "demo@blackfangintel.com"
    DEMO_PASSWORD: str = "demo123"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()

# Database URL validation
if not settings.DATABASE_URL and settings.ENVIRONMENT == "production":
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ DATABASE_URL not set - running in demo mode")

# Subscription plan limits
SUBSCRIPTION_LIMITS = {
    "basic": {
        "competitors": settings.BASIC_PLAN_COMPETITOR_LIMIT,
        "price": settings.BASIC_PLAN_PRICE,
        "alerts_per_month": 100,
        "reports_per_month": 4
    },
    "professional": {
        "competitors": settings.PROFESSIONAL_PLAN_COMPETITOR_LIMIT,
        "price": settings.PROFESSIONAL_PLAN_PRICE,
        "alerts_per_month": 500,
        "reports_per_month": 12
    },
    "enterprise": {
        "competitors": settings.ENTERPRISE_PLAN_COMPETITOR_LIMIT,
        "price": settings.ENTERPRISE_PLAN_PRICE,
        "alerts_per_month": 9999,
        "reports_per_month": 52
    }
}

# User agent strings for web scraping
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# Alert severity levels
ALERT_SEVERITY_LEVELS = {
    "CRITICAL": {
        "priority": 1,
        "color": "#dc2626",
        "requires_immediate_action": True
    },
    "HIGH": {
        "priority": 2, 
        "color": "#f59e0b",
        "requires_immediate_action": True
    },
    "MEDIUM": {
        "priority": 3,
        "color": "#3b82f6", 
        "requires_immediate_action": False
    },
    "LOW": {
        "priority": 4,
        "color": "#10b981",
        "requires_immediate_action": False
    }
}

# Threat levels for competitors
THREAT_LEVELS = {
    "HIGH": {
        "monitoring_frequency": 60,  # minutes
        "alert_threshold": 0.7,
        "color": "#dc2626"
    },
    "MEDIUM": {
        "monitoring_frequency": 180,
        "alert_threshold": 0.5,
        "color": "#f59e0b" 
    },
    "LOW": {
        "monitoring_frequency": 360,
        "alert_threshold": 0.3,
        "color": "#10b981"
    }
}
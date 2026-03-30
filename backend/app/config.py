"""
Configuration management for the Intent-Aware Network Stack.
"""
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Intent-Aware Network Stack"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENV: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./intent_network.db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ML Configuration
    MODEL_PATH: str = "models/trained_models"
    RETRAIN_INTERVAL_HOURS: int = 24
    PREDICTION_THRESHOLD: float = 0.85

    # Network Capture
    CAPTURE_INTERFACE: Optional[str] = None
    CAPTURE_BUFFER_SIZE: int = 65535
    FLOW_TIMEOUT_SECONDS: int = 60

    # QoS Configuration
    QOS_ENABLED: bool = True
    DEFAULT_BANDWIDTH_Mbps: int = 1000
    QUEUE_LIMIT: int = 1000

    # Classification Categories
    CATEGORIES: List[str] = ["interactive", "streaming", "background", "malicious"]
    PRIORITY_LEVELS: dict = {
        "interactive": 1,    # Highest
        "streaming": 2,      # Medium
        "background": 3,     # Low
        "malicious": 4       # Blocked
    }

    # Bandwidth Allocation (percentage)
    BANDWIDTH_ALLOCATION: dict = {
        "interactive": 50,    # 50% for real-time traffic
        "streaming": 30,        # 30% for streaming
        "background": 15,       # 15% for background
        "malicious": 0          # 0% - blocked
    }

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
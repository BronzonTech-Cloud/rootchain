import os
from typing import Dict, Any
from pydantic import BaseSettings, validator
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_KEY: str
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ENVIRONMENT: str = "development"
    
    # Rate Limiting
    RATE_LIMIT: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Cache Settings
    CACHE_TYPE: str = "memory"  # "memory" or "redis"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    BALANCE_CACHE_TTL: int = 60
    GAS_PRICE_CACHE_TTL: int = 10
    
    # Stripe Settings
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    ROOT_PRICE_USD: float = 90.0  # $90 per ROOT/tROOT
    
    # Blockchain Settings
    MAINNET_RPC: str = "http://localhost:8545"
    TESTNET_RPC: str = "http://localhost:8546"
    GAS_LIMIT: int = 21000
    MIN_GAS_PRICE: float = 0.00001
    
    # Monitoring Settings
    PROMETHEUS_PORT: int = 8001
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/wallet.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # Security Settings
    CORS_ORIGINS: list = ["*"]
    MIN_MNEMONIC_LENGTH: int = 24
    MAX_MNEMONIC_LENGTH: int = 500
    MIN_ADDRESS_LENGTH: int = 30
    MAX_ADDRESS_LENGTH: int = 50
    
    # Network Settings
    NETWORKS: Dict[str, Dict[str, Any]] = {
        "mainnet": {
            "prefix": "rtc",
            "symbol": "ROOT",
            "treasury": "rtc_treasury",
            "coin_type": 8888
        },
        "testnet": {
            "prefix": "trtc",
            "symbol": "tROOT",
            "treasury": "trtc_treasury",
            "coin_type": 8889
        }
    }
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v: str) -> str:
        if v not in ["development", "staging", "production"]:
            raise ValueError("Invalid environment")
        return v
    
    @validator("CACHE_TYPE")
    def validate_cache_type(cls, v: str) -> str:
        if v not in ["memory", "redis"]:
            raise ValueError("Invalid cache type")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Create settings instance
settings = get_settings() 
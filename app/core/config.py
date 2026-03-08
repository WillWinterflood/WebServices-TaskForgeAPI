import os


class Settings:
    app_name = os.getenv("APP_NAME", "Recipe Intelligence API")
    api_v1_prefix = os.getenv("API_V1_PREFIX", "/api/v1")
    environment = os.getenv("ENVIRONMENT", "development")
    database_url = os.getenv("DATABASE_URL", "sqlite:///./recipe_intelligence.db")

    jwt_secret_key = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    redis_enabled = os.getenv("REDIS_ENABLED", "true").lower() in ["1", "true", "yes", "on"]
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_cache_ttl_seconds = int(os.getenv("REDIS_CACHE_TTL_SECONDS", "120"))


settings = Settings()

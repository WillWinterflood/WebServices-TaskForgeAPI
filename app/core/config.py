import os
from pathlib import Path


def normalize_database_url(database_url):
    if not database_url:
        return database_url

    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)

    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return database_url


def build_default_database_url():
    if os.name == "nt":
        base_dir = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "RecipeIntelligenceAPI"
    else:
        base_dir = Path.home() / ".recipe-intelligence-api"

    base_dir.mkdir(parents=True, exist_ok=True)
    database_path = (base_dir / "recipe_intelligence.db").resolve()
    return f"sqlite:///{database_path.as_posix()}"


class Settings:
    app_name = os.getenv("APP_NAME", "Healthy Recipe Search and Macro Recommendation API")
    api_v1_prefix = os.getenv("API_V1_PREFIX", "/api/v1")
    environment = os.getenv("ENVIRONMENT", "development")
    database_url = normalize_database_url(os.getenv("DATABASE_URL")) or build_default_database_url()

    jwt_secret_key = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    redis_enabled = os.getenv("REDIS_ENABLED", "true").lower() in ["1", "true", "yes", "on"]
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_cache_ttl_seconds = int(os.getenv("REDIS_CACHE_TTL_SECONDS", "120"))


settings = Settings()

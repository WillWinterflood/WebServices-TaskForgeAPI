import os

class Settings:
    app_name = os.getenv("APP_NAME", "Recipe Intelligence API")
    api_v1_prefix = os.getenv("API_V1_PREFIX", "/api/v1")
    environment = os.getenv("ENVIRONMENT", "development")
    database_url = os.getenv("DATABASE_URL", "sqlite:///./recipe_intelligence.db")

settings = Settings()


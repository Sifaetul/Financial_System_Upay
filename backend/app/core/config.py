from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "UPAY NEXUS AI"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    ENVIRONMENT: str = "development"
    
    # Placeholders for future phases
    DATABASE_URI: str = "postgresql+psycopg2://user:password@localhost:5432/upay_nexus"
    REDIS_URI: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "placeholder-secret-do-not-use-in-prod"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @model_validator(mode="after")
    def validate_production_safety(self):
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == "placeholder-secret-do-not-use-in-prod" or len(self.SECRET_KEY) < 32:
                raise ValueError("Required production configuration is missing or unsafe (SECRET_KEY).")
            if "localhost" in self.DATABASE_URI and not os.environ.get("ALLOW_LOCALHOST_DB"):
                raise ValueError("Required production configuration is unsafe (localhost DB).")
        return self

settings = Settings()

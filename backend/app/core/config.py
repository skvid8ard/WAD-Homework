from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str
    DATABASE_URL: str
    REDIS_URL: str
    
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""

    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = ""

    LLM_MODEL_PATH: str = "/ai-models/qwen.gguf"

    ENVIRONMENT: str = "production" 

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587  # Стандартный порт TLS
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""

    model_config = SettingsConfigDict(
        env_file=[".env", "../.env", "../../.env"], 
        extra="ignore"
    )

settings = Settings()
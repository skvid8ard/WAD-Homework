from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str
    DATABASE_URL: str
    REDIS_URL: str
    
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
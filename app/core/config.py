from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    admin_password: str = "default_admin_password"
    naver_client_id: str = ""
    naver_client_secret: str = ""
    gemini_api_key: str = ""
    telegram_bot_token: str = ""
    database_url: str = "sqlite:///./data/articles.db"
    
    model_config = SettingsConfigDict(env_file=".env")

@lru_cache()
def get_settings():
    return Settings()

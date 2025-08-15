from pydantic_settings import BaseSettings

from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str
    MODEL_NAME: str = "DeepSeek-R1"
    EMBEDDING_MODEL_NAME: str = "text-embedding-ada-002"
    EMBEDDING_API_KEY: Optional[str] = None
    API_BASE: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()

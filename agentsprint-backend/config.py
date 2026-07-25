import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    groq_model: str = "llama-3.1-70b-versatile"
    openai_model: str = "gpt-4o-mini"
    
    graph_db_path: str = "data/haceb_graph.gpickle"
    fuzzy_threshold: int = 85
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
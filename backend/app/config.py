from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_env: str = "development"
    api_port: int = 8000
    frontend_origin: str = "http://localhost:3000"

    database_url: str = "sqlite:///./process_automation.db"
    redis_url: str = ""
    ai_provider: str = "azure_openai"
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_api_version: str = "2024-08-01-preview"
    azure_openai_deployment: str = ""

    auth_provider: str = "dev"
    auth_jwks_url: str = ""
    auth_jwt_issuer: str = ""
    auth_jwt_audience: str = "authenticated"
    auth_jwt_algorithms: str = "RS256"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()

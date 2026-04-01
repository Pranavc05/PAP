from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_env: str = "development"
    api_port: int = 8000
    frontend_origin: str = "http://localhost:3000"

    database_url: str = "sqlite:///./process_automation.db"
    redis_url: str = ""
    openai_api_key: str = ""

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwks_url: str = ""

    auth_provider: str = "dev"
    auth_jwks_url: str = ""
    auth_jwt_issuer: str = ""
    auth_jwt_audience: str = "authenticated"
    auth_jwt_algorithms: str = "RS256"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar, Dict

class Settings(BaseSettings):
    # --- Database ---
    database_url: str
    # --- LLM ---
    max_llm_iterations: int = 5
    max_tool_retries: int = 2
    # Hardcoded tenants for seeding
    HARDCODED_TENANTS: ClassVar[Dict[str, dict]] = {
        "tenant1-key": {"id": 1, "name": "Tenant 1"},
        "tenant2-key": {"id": 2, "name": "Tenant 2"},
        "tenant3-key": {"id": 3, "name": "Tenant 3"},
    }
    # Supported LLM models
    SUPPORTED_LLM_MODELS: ClassVar[list[str]] = [
        "gpt-4o",
        "gemini",
    ]
    # .env settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
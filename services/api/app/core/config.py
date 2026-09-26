from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    supabase_url: str
    supabase_service_role_key: str

    llama_cloud_api_key: str | None = None
    openai_api_key: str | None = None

    # Current demo mode: use deterministic mock extraction.
    # Set to "gpt4o" later when API credits are available.
    extraction_provider: str = "mock"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
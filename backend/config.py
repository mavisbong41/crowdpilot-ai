from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "crowdpilot"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    cors_origins: str = "https://crowdpilot-ai-tau.vercel.app, http://localhost:5173"

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "models/gemini-3-flash-preview"
    gemini_temperature: float = 0.2

    agents_use_gemini: bool = True
    agent_fallback_to_rules: bool = True

    # Demo Mode
    demo_mode: bool = False

    # Logging
    log_level: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Autonomous Multi-Agent Workflow Platform"
    gemini_api_key: str = Field(default="", validation_alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-3.5-flash-lite", validation_alias="GEMINI_MODEL")
    pinecone_api_key: str = Field(default="", validation_alias="PINECONE_API_KEY")
    pinecone_index: str = Field(default="multi-agent-memory", validation_alias="PINECONE_INDEX")
    n8n_webhook_url: str = Field(default="", validation_alias="N8N_WEBHOOK_URL")
    use_crewai: bool = Field(default=True, validation_alias="USE_CREWAI")
    use_pinecone: bool = Field(default=False, validation_alias="USE_PINECONE")
    notify_n8n: bool = Field(default=False, validation_alias="NOTIFY_N8N")
    data_dir: Path = Path("data")
    max_retries: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)

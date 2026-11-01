from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root directory
BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    # Application information
    APP_NAME: str = "ResearchMate AI"
    API_V1_PREFIX: str = "/api/v1"

    # Hugging Face configuration
    HF_TOKEN: str = ""
    
    # Google Gemini configuration
    GOOGLE_GEMINI_TOKEN: str = ""
    LLM_MODEL: str = "gemini-3.8-flash"

    # Embedding model
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ChromaDB storage
    CHROMA_DB_PATH: str = str(BASE_DIR / "backend" / "storage" / "chroma_db")

    # Document processing
    MAX_UPLOAD_SIZE_MB: int = 20
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150

    # Environment configuration
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
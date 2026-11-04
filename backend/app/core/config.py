from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root directory
BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    # Application information
    APP_NAME: str = "ResearchMate AI"
    API_V1_PREFIX: str = "/api/v1"

    # Research conversation database
    DATABASE_URL: str = (
        f"sqlite:///{(BASE_DIR / 'backend' / 'storage' / 'research_history.db').as_posix()}"
    )

    # Google Gemini configuration
    GOOGLE_GEMINI_TOKEN: str = ""
    LLM_MODEL: str = "gemini-3.5-flash-lite"

    # Embedding model
    # Gemini embedding configuration
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_DIMENSION: int = 768

    # ChromaDB storage
    CHROMA_DB_PATH: str = str(
        BASE_DIR / "backend" / "storage" / "chroma_db"
    )
    CHROMA_COLLECTION_NAME: str = "research_documents_gemini"

    # Permanent PDF document storage
    DOCUMENT_STORAGE_PATH: str = str(
        BASE_DIR / "backend" / "storage" / "documents"
    )

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
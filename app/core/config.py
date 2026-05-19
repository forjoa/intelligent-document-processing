from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    MAX_FILE_SIZE_MB: int = 20
    MAX_PAGES: int = 50
    OCR_CONFIDENCE_THRESHOLD: float = 0.8
    CLASSIFICATION_MIN_CONFIDENCE: float = 0.4
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    IVFFLAT_LISTS: int = 100
    SEARCH_DEFAULT_TOP_N: int = 5

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

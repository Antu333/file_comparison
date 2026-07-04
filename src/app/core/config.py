from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from functools import lru_cache


class Settings(BaseSettings):
    GEMINI_API_KEY: str = Field(..., alias="GEMINI_API_KEY")
    BASE_DIR: Path = Path(__file__).resolve().parents[3]
    OUTPUTS_DIR: Path = BASE_DIR / "outputs"
    MERGE_ON_COLUMN: str = "sl no"

    class Config:
        env_file = ".env"
        extra = "ignore"



@lru_cache()
def get_settings() -> Settings:
    return Settings()

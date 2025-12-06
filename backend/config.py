# Nion Orchestration Engine MVP - Configuration

import os
from pathlib import Path
from pydantic import BaseModel, Field

# Base directories
BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / "storage"
OUTPUT_DIR = BASE_DIR / "output"
SAMPLES_DIR = BASE_DIR / "samples"

# Create directories if they don't exist
STORAGE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
SAMPLES_DIR.mkdir(exist_ok=True)


class GroqConfig(BaseModel):
    """Configuration for Groq API (LLaMA 3 70B)"""
    api_key: str = Field(
        default_factory=lambda: os.getenv("GROQ_API_KEY", "")
    )
    base_url: str = "https://api.groq.com/openai/v1"
    model: str = "llama-3.3-70b-versatile"
    timeout: float = 60.0
    max_retries: int = 3


class StorageConfig(BaseModel):
    """Configuration for SQLite storage"""
    db_path: Path = STORAGE_DIR / "db.sqlite"


class Config(BaseModel):
    """Main application configuration"""
    llm: GroqConfig = Field(default_factory=GroqConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    output_dir: Path = OUTPUT_DIR
    samples_dir: Path = SAMPLES_DIR
    
    # L1 orchestration settings
    max_tasks_per_message: int = 10
    default_priority: str = "medium"


# Global config instance
config = Config()

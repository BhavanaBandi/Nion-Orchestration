# Nion Orchestration Engine MVP - Configuration

import os
from pathlib import Path
from pydantic import BaseModel, Field

# Load .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system env vars

# Base directories
BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / "storage"
OUTPUT_DIR = BASE_DIR / "output"
SAMPLES_DIR = BASE_DIR / "samples"

# Create directories if they don't exist
STORAGE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
SAMPLES_DIR.mkdir(exist_ok=True)


class LLMConfig(BaseModel):
    """Configuration for LLM Provider (Gemini, Groq, or OpenAI)"""
    provider: str = Field(
        default_factory=lambda: os.getenv("LLM_PROVIDER", "gemini")
    )
    api_key: str = Field(default="")
    base_url: str = Field(default="")
    model: str = Field(default="")
    timeout: float = 60.0
    max_retries: int = 3

    def __init__(self, **data):
        super().__init__(**data)
        
        # Auto-configure based on provider if not explicitly set
        if self.provider == "openai":
            self.api_key = self.api_key or os.getenv("OPENAI_API_KEY", "")
            self.base_url = self.base_url or "https://api.openai.com/v1"
            self.model = self.model or "gpt-4o"
        elif self.provider == "gemini":
            self.api_key = self.api_key or os.getenv("GEMINI_API_KEY", "")
            # Gemini SDK doesn't use base_url in the same way, but we keep it for consistency or custom endpoints
            self.base_url = self.base_url or "" 
            self.model = self.model or "gemini-2.5-flash"
        else:
            # Default to Groq
            self.api_key = self.api_key or os.getenv("GROQ_API_KEY", "")
            self.base_url = self.base_url or "https://api.groq.com/openai/v1"
            self.model = self.model or "llama-3.3-70b-versatile"


class StorageConfig(BaseModel):
    """Configuration for SQLite storage"""
    db_path: Path = STORAGE_DIR / "db.sqlite"


class Config(BaseModel):
    """Main application configuration"""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    output_dir: Path = OUTPUT_DIR
    samples_dir: Path = SAMPLES_DIR
    
    # L1 orchestration settings
    max_tasks_per_message: int = 10
    default_priority: str = "medium"


# Global config instance
config = Config()

"""Application settings and configuration management."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ModelConfig:
    """Model-related configuration."""

    default_model: str = "meta-llama/Llama-2-7b-hf"
    cache_dir: Optional[Path] = None
    device: str = "mps"  # For Apple Silicon (M-series)
    max_length: int = 512
    batch_size: int = 8
    precision: str = "float16"

    def __post_init__(self):
        """Initialize computed fields."""
        if self.cache_dir is None:
            self.cache_dir = Path.home() / ".cache" / "huggingface"


@dataclass
class TrainingConfig:
    """Training-related configuration."""

    learning_rate: float = 2e-5
    num_epochs: int = 3
    warmup_steps: int = 500
    weight_decay: float = 0.01
    logging_steps: int = 100
    save_steps: int = 1000
    eval_steps: int = 500
    output_dir: Path = field(default_factory=lambda: Path("./outputs"))

    def __post_init__(self):
        """Ensure output directory exists."""
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class DataConfig:
    """Data-related configuration."""

    data_dir: Path = field(default_factory=lambda: Path("./data"))
    dataset_name: Optional[str] = None
    train_split: str = "train"
    validation_split: str = "validation"
    test_split: str = "test"
    max_samples: Optional[int] = None

    def __post_init__(self):
        """Ensure data directory exists."""
        self.data_dir = Path(self.data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class Settings:
    """Main application settings."""

    # Environment
    env: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # Hugging Face Hub
    hf_token: Optional[str] = field(default_factory=lambda: os.getenv("HF_TOKEN"))
    hf_home: Path = field(default_factory=lambda: Path(os.getenv("HF_HOME", str(Path.home() / ".cache" / "huggingface"))))

    # Sub-configurations
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    data: DataConfig = field(default_factory=DataConfig)

    # API settings (if applicable)
    api_host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    api_port: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))

    # Performance
    num_workers: int = field(default_factory=lambda: int(os.getenv("NUM_WORKERS", "4")))

    def __post_init__(self):
        """Initialize and validate settings."""
        self.hf_home = Path(self.hf_home)
        self.hf_home.mkdir(parents=True, exist_ok=True)

        # Set HF_HOME environment variable for transformers/datasets
        os.environ["HF_HOME"] = str(self.hf_home)

        if self.hf_token:
            os.environ["HF_TOKEN"] = self.hf_token


# Global settings instance
_settings: Optional[Settings] = None


def get_settings(reload: bool = False) -> Settings:
    """
    Get the global settings instance (singleton pattern).

    Args:
        reload: If True, reload settings from environment

    Returns:
        Settings instance
    """
    global _settings

    if _settings is None or reload:
        _settings = Settings()

    return _settings


def load_settings_from_env() -> Settings:
    """
    Load settings from environment variables.

    Returns:
        Settings instance
    """
    return get_settings(reload=True)

from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration using Pydantic for validation and environment variable support."""

    # Model Configuration
    tts_model_name: str = Field(
        default="openbmb/VoxCPM-0.5B", description="Text To Speech model"
    )
    model_cache_dir: Optional[str] = Field(
        default=None, description="Directory to cache models"
    )

    # TTS Default Parameters
    default_inference_timesteps: int = Field(
        default=10, ge=1, le=100, description="Default number of inference timesteps"
    )
    default_cfg_value: float = Field(
        default=2.0,
        ge=0.1,
        le=10.0,
        description="Default CFG (Classifier-Free Guidance) value",
    )
    default_retry_max_times: int = Field(
        default=3, ge=1, le=10, description="Maximum number of retry attempts"
    )
    default_retry_ratio_threshold: float = Field(
        default=6.0, ge=1.0, le=20.0, description="Threshold ratio for retry logic"
    )

    # Audio Settings
    sample_rate: int = Field(default=16000, description="Audio sample rate in Hz")
    audio_format: str = Field(default="WAV", description="Default audio format")

    # Application Settings
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()

    # API Settings
    max_text_length: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Maximum text length for TTS processing",
    )
    allowed_audio_formats: List[str] = Field(
        default=[".wav", ".mp3", ".flac"],
        description="List of allowed audio file formats",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Map environment variables to field names
        fields = {
            "tts_model_name": {"env": "TTS_MODEL_NAME"},
            "model_cache_dir": {"env": "MODEL_CACHE_DIR"},
            "default_inference_timesteps": {"env": "DEFAULT_INFERENCE_TIMESTEPS"},
            "default_cfg_value": {"env": "DEFAULT_CFG_VALUE"},
            "default_retry_max_times": {"env": "DEFAULT_RETRY_MAX_TIMES"},
            "default_retry_ratio_threshold": {"env": "DEFAULT_RETRY_RATIO_THRESHOLD"},
            "sample_rate": {"env": "SAMPLE_RATE"},
            "audio_format": {"env": "AUDIO_FORMAT"},
            "debug": {"env": "DEBUG"},
            "log_level": {"env": "LOG_LEVEL"},
            "max_text_length": {"env": "MAX_TEXT_LENGTH"},
            "allowed_audio_formats": {"env": "ALLOWED_AUDIO_FORMATS"},
        }


# Create a global settings instance
settings = Settings()

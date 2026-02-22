"""Configuration management for the trade war simulation."""

import os
from dataclasses import dataclass
from typing import Dict, Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class SimulationConfig:
    """Configuration parameters for simulation execution."""

    years: int
    steps_per_year: int
    random_seed: int
    output_dir: str


@dataclass
class LLMConfig:
    """Configuration for LLM API connections."""

    provider: str
    api_key: str
    model: str
    temperature: float
    max_tokens: int


@dataclass
class APIConfig:
    """Configuration for the API server."""

    host: str
    port: int


@dataclass
class TradePolicyConfig:
    """Configuration for trade policy dynamics in the simulation."""

    enable_trade_diversion: bool
    trade_diversion_intensity: float
    max_trade_diversion_share: float
    us_indonesia_art_start_year: int
    us_indonesia_access_preference: float


@dataclass
class Config:
    """Main configuration container."""

    simulation: SimulationConfig
    llm: LLMConfig
    api: APIConfig
    trade_policy: TradePolicyConfig
    log_level: str
    log_file: Optional[str] = None


def _get_bool_env(name: str, default: bool) -> bool:
    """Read boolean environment variables safely."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_config() -> Config:
    """
    Load configuration from environment variables.
    
    Returns:
        Config: Complete configuration object
    """
    llm_provider = os.getenv("LLM_PROVIDER", "litellm")
    # Pick the right API key based on the configured provider
    if llm_provider == "anthropic":
        _default_api_key = os.getenv("ANTHROPIC_API_KEY", "")
    elif llm_provider in ("litellm", "openai"):
        _default_api_key = os.getenv("OPENAI_API_KEY", "") or os.getenv("LITELLM_API_KEY", "")
    else:
        _default_api_key = os.getenv("LLM_API_KEY", "")

    return Config(
        simulation=SimulationConfig(
            years=int(os.getenv("SIMULATION_YEARS", "5")),
            steps_per_year=int(os.getenv("SIMULATION_STEPS_PER_YEAR", "4")),
            random_seed=int(os.getenv("RANDOM_SEED", "42")),
            output_dir=os.getenv("OUTPUT_DIR", "simulation_results"),
        ),
        llm=LLMConfig(
            provider=llm_provider,
            api_key=os.getenv("LLM_API_KEY", _default_api_key),
            model=os.getenv("LLM_MODEL", "gpt-4o"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1024")),
        ),
        api=APIConfig(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8000")),
        ),
        trade_policy=TradePolicyConfig(
            enable_trade_diversion=_get_bool_env("ENABLE_TRADE_DIVERSION", True),
            trade_diversion_intensity=float(os.getenv("TRADE_DIVERSION_INTENSITY", "0.35")),
            max_trade_diversion_share=float(os.getenv("MAX_TRADE_DIVERSION_SHARE", "0.25")),
            us_indonesia_art_start_year=int(os.getenv("US_INDONESIA_ART_START_YEAR", "2026")),
            us_indonesia_access_preference=float(os.getenv("US_INDONESIA_ACCESS_PREFERENCE", "0.15")),
        ),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=os.getenv("LOG_FILE"),
    )


# Default configuration instance
config = load_config()

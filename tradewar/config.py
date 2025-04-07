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
class Config:
    """Main configuration container."""

    simulation: SimulationConfig
    llm: LLMConfig
    api: APIConfig
    log_level: str
    log_file: Optional[str] = None


def load_config() -> Config:
    """
    Load configuration from environment variables.
    
    Returns:
        Config: Complete configuration object
    """
    return Config(
        simulation=SimulationConfig(
            years=int(os.getenv("SIMULATION_YEARS", "5")),
            steps_per_year=int(os.getenv("SIMULATION_STEPS_PER_YEAR", "4")),
            random_seed=int(os.getenv("RANDOM_SEED", "42")),
            output_dir=os.getenv("OUTPUT_DIR", "simulation_results"),
        ),
        llm=LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "openai"),
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("LLM_MODEL", "gpt-4"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1024")),
        ),
        api=APIConfig(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8000")),
        ),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=os.getenv("LOG_FILE"),
    )


# Default configuration instance
config = load_config()

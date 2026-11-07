"""
Configuration loader and validator for OLX Deal Sniper.
"""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from models import SearchTarget

# Load environment variables from .env file
load_dotenv()


class TelegramConfig(BaseModel):
    bot_token: str = Field(default="")
    chat_id: str = Field(default="")


class MonitoringConfig(BaseModel):
    check_interval_seconds: int = 45
    jitter_seconds: int = 15
    offers_limit: int = 30
    notify_on_startup: bool = False


class RegionsConfig(BaseModel):
    priority_region_id: int = 13
    priority_region_name: str = "Івано-Франківськ"
    priority_cities: list[str] = Field(
        default_factory=lambda: [
            "івано-франківськ",
            "калуш",
            "коломия",
            "надвірна",
            "яремче",
            "долина",
            "бурштин",
            "богородчани",
        ]
    )


class DatabaseConfig(BaseModel):
    path: str = "data/seen_ads.db"


class FilteringConfig(BaseModel):
    skip_above_market: bool = True
    min_discount_percent: float = 0.0


class AppConfig(BaseModel):
    telegram: TelegramConfig
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    regions: RegionsConfig = Field(default_factory=RegionsConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    filtering: FilteringConfig = Field(default_factory=FilteringConfig)
    global_stop_words: list[str] = Field(default_factory=list)
    searches: list[SearchTarget] = Field(default_factory=list)


def load_config(config_path: str = "config.yaml") -> AppConfig:
    """
    Loads configuration from YAML file and overrides sensitive tokens from environment.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        raw_data = yaml.safe_load(f) or {}

    config = AppConfig(**raw_data)

    # Override Telegram credentials from environment if available
    env_token = os.getenv("TELEGRAM_BOT_TOKEN")
    env_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if env_token:
        config.telegram.bot_token = env_token.strip()
    if env_chat_id:
        config.telegram.chat_id = env_chat_id.strip()

    # Ensure database directory exists
    db_dir = Path(config.database.path).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    return config

from pathlib import Path
from typing import Literal

from loguru import logger
from pydantic_settings import BaseSettings

type LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
type ByteSize = Literal["TB", "GB", "MB", "KB", "B"]


class Settings(BaseSettings):
    DEBUG: bool = False
    LOG_LEVEL: LogLevel | int = "INFO"

    BASE_PATH: Path = Path.home()
    LIST_PATH: Path = Path.home() / "selection"
    BYTE_SIZE: ByteSize = "MB"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings():
    return Settings()


def log_settings():
    settings = get_settings()

    if not settings.DEBUG:
        return

    for key, value in get_settings():
        logger.info(f"Settings.{key}={value}")

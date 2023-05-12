import json
from typing import Any
from pathlib import Path
from pydantic import (
    BaseSettings
)
from models.Website import Website


def json_config_settings_source(settings: BaseSettings) -> dict[str, Any]:
    return json.loads(Path('config.json').read_text('utf-8'))


class Settings(BaseSettings):
    checking_period_seconds: int
    log_filename: str
    websites: list[Website]

    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings
        ):
            return (
                init_settings,
                json_config_settings_source,
                env_settings,
                file_secret_settings
            )

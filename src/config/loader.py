import json
import os
from pathlib import Path
from .models import Config

_config: Config = None  # cached config instance

def get_config() -> Config:
    global _config
    if _config is None:
        config_path = os.getenv('CONFIG_PATH', None)
        if not config_path:
            # default to config/config.json next to loader.py
            config_path = Path(__file__).parent / 'config.json'
        print(f"[DEBUG] Loading config from: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        _config = Config(**data)
    return _config 
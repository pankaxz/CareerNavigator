import yaml
import os
from typing import Dict, Any

class Config:
    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._load_config()
        return cls._instance

    @classmethod
    def _load_config(cls):
        # Assuming run from root DataFactory/
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'settings.yaml')
        # Fallback if running from src?
        if not os.path.exists(config_path):
             config_path = "config/settings.yaml" # Try relative to CWD
        
        try:
            with open(config_path, 'r') as f:
                cls._config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️ Config not found at {config_path}, using defaults.")
            cls._config = {}

    @classmethod
    def get(cls, path: str, default: Any = None) -> Any:
        keys = path.split('.')
        val = cls._config
        for key in keys:
            if isinstance(val, dict):
                val = val.get(key)
            else:
                return default
        return val if val is not None else default

    @property
    def project_root(self) -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def get_abs_path(self, path_key: str) -> str:
        """Resolves a config path relative to the project root."""
        val = self.get(path_key)
        if val and isinstance(val, str) and not os.path.isabs(val):
             return os.path.join(self.project_root, val)
        return val

# Global accessor
cfg = Config()

# Handles config loading/saving
import os
import yaml

class ConfigManager:
    def __init__(self, config_path='config.yaml', env_path='.env'):
        self.config_path = config_path
        self.env_path = env_path
        self.config = {}
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        self.load_env_vars()

    def load_env_vars(self):
        if os.path.exists(self.env_path):
            with open(self.env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        self.config[key] = value

    def get(self, key, default=None):
        return self.config.get(key, default)

config = ConfigManager()

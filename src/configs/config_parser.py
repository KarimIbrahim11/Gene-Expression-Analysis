import yaml
from pathlib import Path

class PathConfigParser:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.config = {}

    def load(self):
        """Load configuration paths from .json or .yaml files."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.file_path}")

        elif self.file_path.suffix in [".yaml", ".yml"]:
            self._load_yaml()
        else:
            raise ValueError(f"Unsupported configuration format: {self.file_path.suffix}")
    
    def _load_yaml(self):
        """Load paths from a .yaml file."""
        with self.file_path.open("r") as f:
            self.config = yaml.safe_load(f)
        self._convert_data_keys_to_paths()

    def get(self, key, default=None):
        """Retrieve an entry from the configuration."""
        return self.config.get(key, default)
    
    def _convert_data_keys_to_paths(self):
        """Convert all data_path in the config to pathlib.Path objects."""
        for key, value in self.config.get("data_paths", {}).items():
            if isinstance(value, str):
                self.config["data_paths"][key] = Path(value)
            elif isinstance(value, list):
                self.config["data_paths"][key] = [Path(v) for v in value]



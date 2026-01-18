from pathlib import Path
from typing import Dict
import logging
import yaml

from medi_tg_analytics.core.project_root import get_project_root

logger = logging.getLogger(__name__)

# -------------------------
# YAML loader
# -------------------------


def _load_yaml(path: Path) -> Dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise ValueError(f"YAML root must be a dict: {path}")
        return data
    except Exception as exc:
        logger.warning("Failed to load config %s: %s", path.name, exc)
        return {}

# -------------------------
# Merge dicts recursively
# -------------------------


def _deep_merge(d1: Dict, d2: Dict) -> Dict:
    """Recursively merge two dicts, overriding d1 with d2"""
    result = dict(d1)
    for k, v in d2.items():
        if (
            k in result
            and isinstance(result[k], dict)
            and isinstance(v, dict)
        ):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result

# -------------------------
# Load all YAML configs from config/
# -------------------------


def load_config(config_dir: Path = None) -> Dict:
    root = get_project_root()
    config_dir = config_dir or (root / "config")

    merged: Dict = {}
    for path in sorted(config_dir.glob("*.yaml")):
        merged = _deep_merge(merged, _load_yaml(path))

    return merged

# -------------------------
# Path registry
# -------------------------


class PathRegistry:
    def __init__(self, root: Path, config: Dict, create_dirs: bool = True):
        self.root = root.resolve()
        self._paths: Dict[str, Dict[str, Path]] = {}
        # Get the paths dict, default to empty if not found
        paths_cfg = config.get("paths", {})

        for section, mapping in paths_cfg.items():
            resolved: Dict[str, Path] = {}
            for key, rel_path in mapping.items():
                path = (self.root / rel_path).resolve()
                if create_dirs:
                    path.mkdir(parents=True, exist_ok=True)
                resolved[key] = path

            # Store in internal dict
            self._paths[section.lower()] = resolved
            # Explicitly set the uppercase attribute for dot notation
            setattr(self, section.upper(), resolved)

    def __getitem__(self, section: str) -> Dict[str, Path]:
        # Allows settings.paths["data"]
        return self._paths[section.lower()]

    def __getattr__(self, name: str) -> Dict[str, Path]:
        # Allows settings.paths.DATA even if setattr had issues
        if name.lower() in self._paths:
            return self._paths[name.lower()]
        raise AttributeError(f"'PathRegistry' has no attribute '{name}'")
# -------------------------
# Central settings
# -------------------------


class Settings:
    """
    Central runtime settings object.
    Access YAML configs via settings.CONFIG and paths via settings.paths.
    """

    def __init__(self, root: Path = None, create_dirs: bool = True):
        self.root = root.resolve() if root else get_project_root()
        self.config: Dict = load_config(config_dir=self.root / "config")
        self.paths: PathRegistry = PathRegistry(
            self.root, self.config, create_dirs)

    def get(self, section: str, default=None):
        return self.config.get(section, default)


# Singleton instance
settings = Settings()
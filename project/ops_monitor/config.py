"""Load and validate user-managed YAML policy without executing arbitrary YAML tags."""
from pathlib import Path
import yaml

class ConfigurationError(ValueError):
    pass


def load_config(path: Path):
    try:
        config = yaml.safe_load(path.read_text(encoding='utf-8'))
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigurationError(f'Cannot read configuration {path}: {exc}') from exc
    if not isinstance(config, dict):
        raise ConfigurationError('Config must be a YAML mapping')
    defaults, services = config.get('defaults'), config.get('services')
    if not isinstance(defaults, dict) or not isinstance(services, list) or not services:
        raise ConfigurationError('Expected defaults mapping and non-empty services list')
    for k in ('timeout_seconds', 'max_attempts', 'max_latency_ms'):
        if not isinstance(defaults.get(k), (int, float)) or isinstance(defaults.get(k), bool) or defaults[k] <= 0:
            raise ConfigurationError(f'defaults.{k} must be a positive number')
    ids = set()
    for item in services:
        if not isinstance(item, dict) or not isinstance(item.get('id'), str) or not item['id']:
            raise ConfigurationError('Each service must have a non-empty id')
        if item['id'] in ids:
            raise ConfigurationError(f'Duplicate service id: {item["id"]}')
        ids.add(item['id'])
        if not isinstance(item.get('owner'), str) or not item['owner']:
            raise ConfigurationError(f'Missing owner for {item["id"]}')
        if not isinstance(item.get('critical'), bool):
            raise ConfigurationError(f'critical must be boolean for {item["id"]}')
        if 'max_latency_ms' in item and (not isinstance(item['max_latency_ms'], (int, float)) or item['max_latency_ms'] <= 0):
            raise ConfigurationError(f'Invalid max_latency_ms for {item["id"]}')
    return config

#!/usr/bin/env python3
"""Run from repository root; change the thresholds and observe the report."""
import json
from collections import Counter
from pathlib import Path
import yaml

inventory = json.loads(Path('data/inventory.json').read_text())
servers = inventory['servers']
print('Production hosts:', [s['name'] for s in servers if s.get('environment') == 'production'])
print('Host counts by region:', dict(Counter(s['region'] for s in servers)))

config_path = Path('exercises/monitor_config.yaml')
config = yaml.safe_load(config_path.read_text())
print('Configured services:', [s['id'] for s in config['services']])
print('Default timeout:', config['defaults']['timeout_seconds'])
# In memory only: do not overwrite instructor's source by accident.
config['defaults']['timeout_seconds'] = 3
print('Modified YAML (comments may not be preserved):')
print(yaml.safe_dump(config, sort_keys=False))

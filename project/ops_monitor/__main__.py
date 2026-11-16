"""Run with python -m ops_monitor from the project directory."""
import argparse
import logging
import os
from pathlib import Path
import sys
from .client import PlatformClient, PlatformError
from .config import ConfigurationError, load_config
from .evaluate import evaluate
from .report import print_summary, write_json
from .storage import save_run


def main(argv=None):
    parser = argparse.ArgumentParser(description='Configuration-driven service operations monitor')
    parser.add_argument('--config', type=Path, default=Path('config/services.yaml'))
    parser.add_argument('--json-out', type=Path, default=Path('out/latest.json'))
    parser.add_argument('--database', type=Path, default=Path('out/history.sqlite3'))
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s %(name)s: %(message)s')
    token = os.getenv('PLATFORM_TOKEN')
    if not token:
        print('CONFIG ERROR: PLATFORM_TOKEN environment variable is required', file=sys.stderr)
        return 1
    try:
        config = load_config(args.config)
        timeout = float(os.getenv('MONITOR_TIMEOUT', config['defaults']['timeout_seconds']))
        if timeout <= 0: raise ValueError('timeout must be positive')
        client = PlatformClient(os.getenv('PLATFORM_URL', 'http://127.0.0.1:8765'),
            token, timeout=timeout, attempts=int(config['defaults']['max_attempts']))
        try:
            services = client.inventory()
            incidents = client.incidents()
        finally:
            client.close()
        findings = evaluate(services, incidents, config)
        print_summary(findings)
        write_json(args.json_out, findings)
        save_run(args.database, findings)
        print(f'JSON report: {args.json_out} | History: {args.database}')
        return 2 if any(f.severity == 'critical' for f in findings) else 0
    except (ConfigurationError, ValueError, PlatformError, KeyError, TypeError, OSError) as exc:
        logging.error('Monitor failed: %s', exc)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())

# An application is experiencing failures. We need to analyze logs, identify patterns and detect recurring errors within a time window.

#!/usr/bin/env python3
"""Incident triage across rotated service logs, with a sliding time window."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import sys

LINE = re.compile(r'^(?P<timestamp>\S+) level=(?P<level>\w+) service=(?P<service>[\w-]+) code=(?P<code>[\w-]+) request_id=(?P<request>\S+) msg="(?P<message>.*)"$')

def parse_files(folder):
    records = []
    skipped = 0
    for path in sorted(folder.glob('*.log')):
        with path.open() as stream:
            for line_number, line in enumerate(stream, 1):
                match = LINE.match(line.strip())
                if not match:
                    print(f'WARN: skipped malformed line {path}:{line_number}', file=sys.stderr)
                    skipped += 1
                    continue
                entry = match.groupdict()
                try:
                    entry['when'] = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                except ValueError:
                    skipped += 1
                    continue
                records.append(entry)
    records.sort(key=lambda e: e['when'])
    return records, skipped


def detect_bursts(records, window_seconds, threshold):
    by_signature = defaultdict(list)
    for row in records:
        if row['level'] == 'ERROR':
            by_signature[(row['service'], row['code'])].append(row['when'])
    bursts = []
    for (service, code), times in sorted(by_signature.items()):
        left = 0
        for right, moment in enumerate(times):
            while moment - times[left] > timedelta(seconds=window_seconds):
                left += 1
            if right-left+1 >= threshold:
                bursts.append((service, code, right-left+1, times[left].isoformat()))
                break
    return bursts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--logs', type=Path, default=Path('data/logs'))
    parser.add_argument('--window', type=int, default=120, help='seconds')
    parser.add_argument('--threshold', type=int, default=3)
    args = parser.parse_args()
    if not args.logs.is_dir() or args.window < 1 or args.threshold < 1:
        parser.exit(1, 'INPUT ERROR: valid log directory, window and threshold required\n')
    rows, skipped = parse_files(args.logs)
    error_counts = Counter((r['service'], r['code']) for r in rows if r['level'] == 'ERROR')
    print(f'Parsed: {len(rows)} | Skipped: {skipped}')
    for (service, code), count in sorted(error_counts.items()):
        print(f'{service:<22} {code:<20} errors={count}')
    bursts = detect_bursts(rows, args.window, args.threshold)
    for service, code, count, started in bursts:
        print(f'ALERT burst {service}/{code}: >= {count} in {args.window}s (from {started})')
    return 2 if bursts else 0

if __name__ == '__main__':
    raise SystemExit(main())

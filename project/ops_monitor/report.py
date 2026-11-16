"""Present the same facts for humans and downstream automation."""
import json
from pathlib import Path


def print_summary(findings):
    print(f'Operational findings: {len(findings)}')
    if not findings: print('All configured services meet policy')
    for finding in findings:
        print(f'[{finding.severity.upper():8}] {finding.service_id:<22} owner={finding.owner}')
        print(f'           reasons={", ".join(finding.reasons)} incidents={",".join(finding.incident_ids) or "-"}')


def write_json(path: Path, findings):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'findings': [f.as_dict() for f in findings],
        'finding_count': len(findings)}, indent=2) + '\n', encoding='utf-8')

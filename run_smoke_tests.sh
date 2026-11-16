#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m compileall -q scenario1_inventory scenario2_api scenario3_logs shared project exercises
python3 scenario1_inventory/audit.py --output /tmp/devops-inventory-report.json >/tmp/devops-s1.out && s1=0 || s1=$?
[[ $s1 == 2 ]] || { echo "Scenario 1 expected policy violations; got $s1"; exit 1; }
python3 scenario3_logs/analyze.py >/tmp/devops-s3.out && s3=0 || s3=$?
[[ $s3 == 2 ]] || { echo "Scenario 3 expected alerts; got $s3"; exit 1; }
(cd project && python3 -m unittest discover -s tests -v)
echo 'Offline smoke tests succeeded. For API checks start: python3 shared/mock_platform.py'

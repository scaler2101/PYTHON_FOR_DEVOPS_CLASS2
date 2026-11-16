# Python for DevOps 2 — teaching kit

**Training exercises use synthetic inventory/logs and a localhost simulated service platform.** No cloud account, Docker or Kubernetes is needed.

## What is included?

| Folder / file | Purpose |
|---|---|
| `INSTRUCTOR_CLASS_SCRIPT.md` | Full 140-minute, why-first talk track, terminal commands, learner checkpoints, answers, caveats |
| `Python_for_DevOps_2_Instructor_Guide.docx` | Editable instructor guide |
| `scenario1_inventory/` | Bash + Python infrastructure compliance audit |
| `scenario2_api/` | Bash + Python authenticated API integration, pagination, status/incident join, bounded retries |
| `scenario3_logs/` | Bash + Python operational log analysis and sliding-window alerts |
| `data/` | Inventory snapshot and two log files (including deliberate bad data) |
| `shared/mock_platform.py` | No-dependency local HTTP API simulator |
| `exercises/` | JSON/YAML and library exploration exercises |
| `project/` | Modular Python operations monitor, config, unit test, SQLite history, readme |
| `requirements-demo.txt` | Third-party packages for the scenarios and exercises |
| `run_smoke_tests.sh` | Local offline preflight test |

## Setup

Run from this folder:

```bash
python3 --version                  # Python 3.10+
jq --version                       # jq needed for Bash inventory/API solutions
curl --version                     # curl needed for Bash API solution
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-demo.txt
bash run_smoke_tests.sh
```

Keep **terminal A** running:

```bash
python3 shared/mock_platform.py
```

Use **terminal B** for live demos:

```bash
source .venv/bin/activate
export PLATFORM_TOKEN=training-token
bash scenario1_inventory/audit.sh; echo $?
python scenario1_inventory/audit.py; echo $?
bash scenario2_api/ops_report.sh; echo $?
python scenario2_api/ops_report.py; echo $?
bash scenario3_logs/analyze.sh; echo $?
python scenario3_logs/analyze.py; echo $?
python exercises/structured_data.py
```

Project walkthrough:

```bash
cd project
python -m ops_monitor
status=$?; echo "exit=$status"
python -m json.tool out/latest.json | head
python -m unittest discover -s tests -v
```

**Important:** Exit code **2 is expected** for the supplied violations. `0` means no policy finding; `1` means an input/configuration or request error. Codes are conventions of this kit.

Please read the full instructor guide before running in class. It explains what to say, what to show, the why behind every concept and caveats for experienced learners.

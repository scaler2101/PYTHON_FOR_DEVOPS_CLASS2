# Operations Monitor — company-style demo application

This **training application** models a platform team's daily service-health policy checks. It reads human-editable YAML policy, fetches **paginated** service inventory and incidents from an authenticated local HTTP API, applies business rules with pure Python, prints a summary, writes a JSON report, and persists each run in SQLite. Exit codes: `0` healthy, `2` critical finding, `1` execution/config error. A `2` is an expected result with the supplied intentionally unhealthy sample data.

## Run locally (from the kit repository root)

Terminal A:

```bash
python3 shared/mock_platform.py
```

Terminal B:

```bash
cd project
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export PLATFORM_TOKEN=training-token
python -m ops_monitor --verbose
printf 'exit=%s\n' "$?"
python -m unittest discover -s tests -v
```

### Inspect generated output

```bash
python -m json.tool out/latest.json
python -c "import sqlite3; db=sqlite3.connect('out/history.sqlite3'); print(db.execute('SELECT id, ran_at_utc, critical_count FROM runs ORDER BY id DESC LIMIT 5').fetchall())"
```

### Safety and production discussion

- Token is deliberately fake and only accepted by the localhost training server. Never commit a real token.
- Only the local server is contacted. No cloud account, paid service, Docker or Kubernetes required.
- Config validation is present, but the app does not include full production telemetry, metrics export, secrets integration, security hardening, deployment, concurrency, or all failure modes.
- The `requests` session is a replaceable boundary; policy logic has a unit test without needing a live API.
- SQLite stores historical execution snapshots. A real system may use a database, event stream or monitoring backend depending on scale.
- A failed check and a failed monitor are different: exit code 2 versus 1.

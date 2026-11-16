# Objective — Operational Log Analysis and Incident Detection

## Scenario
An application team suspects recurring failures across services. You have log files from multiple servers and need to identify error patterns and detect bursts of similar errors within a short time window.

## Input
- Log directory: `data/logs/`, containing `*.log` files.
- Log entries include an ISO timestamp and fields such as `level`, `service`, `code`, `request_id`, and `msg`.
- Default burst criteria: **at least 3 ERROR events** for the same `(service, code)` within **120 seconds**.

## Requirements
- Read the supplied log files and parse valid log entries.
- Report the number of parsed and skipped lines.
- Count `ERROR` events grouped by service and error code.
- Detect bursts according to the configured threshold and time window.
- Print an alert for each `(service, code)` pattern that reaches the threshold.
- Allow the threshold and window to be changed without editing the core analysis logic.

## Expected console format

```text
Parsed: <count> | Skipped: <count>
<service> <error-code> errors=<count>
ALERT burst <service>/<error-code>: >= <count> in <window>s
```

The Bash and Python scripts may show alerts with slightly different formatting; the Python version additionally shows the burst's starting timestamp. There is **no JSON report requirement** for this scenario.

**Exit status:** `0` = no burst detected; `1` = invalid input; `2` = at least one burst detected.

## Important implementation assumption
The provided Bash implementation assumes the demonstration logs are ordered appropriately and all timestamps fall within one UTC day. The Python implementation parses complete timestamps and sorts records. Discuss this difference during the comparison.

## Provided implementations
- Bash: `scenario3_logs/analyze.sh`
- Python: `scenario3_logs/analyze.py`

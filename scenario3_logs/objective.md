## Requirements
- Read the supplied log files and parse valid log entries.
- Report the number of parsed and skipped lines.
- Count `ERROR` events grouped by service and error code.
- Detect bursts according to the configured threshold and time window.
- Print an alert for each `(service, code)` pattern that reaches the threshold.
- Allow the threshold and window to be changed without editing the core analysis logic.
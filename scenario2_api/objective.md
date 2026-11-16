# Objective — API-Based Operations Report

## Scenario
An operations team needs a consolidated view of services and their open incidents from an internal platform API. API responses may span multiple pages or fail temporarily, so the reporting tool must handle these conditions reliably.

## Input / setup
- Local training API: `shared/mock_platform.py` (default base URL `http://127.0.0.1:8765`).
- Authenticated endpoints: `/api/v1/services` (paginated with `page` and `limit`) and `/api/v1/incidents`.
- Authentication: environment variable `PLATFORM_TOKEN=training-token` is used by the local simulator.

## Requirements
- Authenticate requests with a bearer token.
- Retrieve **all** service pages, following the API's `next_page` value.
- Retrieve incidents and associate each **open** incident with its matching service ID.
- Handle connection errors, timeouts, and temporary HTTP failures with bounded retries.
- Print each service's ID, health status, latency in milliseconds, and open incident IDs.
- Print a summary of total services and how many have a non-`healthy` status.
- Support exporting a machine-readable JSON report.

## Expected report format
The JSON report is an **array of service objects**. Each retains the service fields returned by the API and adds `open_incidents`, an array of incident IDs. For example:

```json
[
  {
    "id": "example-service",
    "status": "healthy",
    "latency_ms": 120,
    "open_incidents": []
  }
]
```

This is a **format illustration**, not the complete live response. The console shows one line per service followed by `Total: ... | Attention: ...`.

**Exit status:** `0` = all services healthy; `1` = configuration/API error; `2` = report completed with at least one nonhealthy service.

## Provided implementations
- Bash: `scenario2_api/ops_report.sh`
- Python: `scenario2_api/ops_report.py`

Compare the real handling of HTTP, paging, retries, structured responses, and failure paths.

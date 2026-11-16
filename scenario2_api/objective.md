## Requirements
- Authenticate requests with a bearer token.
- Retrieve **all** service pages, following the API's `next_page` value.
- Retrieve incidents and associate each **open** incident with its matching service ID.
- Handle connection errors, timeouts, and temporary HTTP failures with bounded retries.
- Print each service's ID, health status, latency in milliseconds, and open incident IDs.
- Print a summary of total services and how many have a non-`healthy` status.
- Support exporting a machine-readable JSON report.
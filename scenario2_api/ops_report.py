#!/usr/bin/env python3
"""Consolidate paginated service data and incidents from a local platform API."""
import argparse
import json
import os
import sys
import time
import requests


def fetch(session, url, *, params=None, attempts=3, timeout=2):
    for attempt in range(1, attempts + 1):
        try:
            response = session.get(url, params=params, timeout=timeout)
            if response.status_code in {429, 500, 502, 503, 504} and attempt < attempts:
                print(f"retryable HTTP {response.status_code}: attempt {attempt}/{attempts}", file=sys.stderr)
                time.sleep(0.2 * attempt)
                continue
            response.raise_for_status()
            return response.json()
        except (requests.Timeout, requests.ConnectionError) as exc:
            if attempt == attempts: raise
            print(f"temporary network error: {exc} (attempt {attempt}/{attempts})", file=sys.stderr)
            time.sleep(0.2 * attempt)
    raise RuntimeError("unreachable retry state")


def collect(session, base_url, attempts=3):
    services = []
    page = 1
    while True:
        result = fetch(session, f"{base_url}/api/v1/services", params={"page": page, "limit": 2}, attempts=attempts)
        services.extend(result["items"])
        if result.get("next_page") is None: break
        if result["next_page"] <= page: raise ValueError("API pagination did not advance")
        page = result["next_page"]
    incidents = fetch(session, f"{base_url}/api/v1/incidents", attempts=attempts)["items"]
    open_by_service = {}
    for incident in incidents:
        if incident.get("state") == "open":
            open_by_service.setdefault(incident["service_id"], []).append(incident["id"])
    return [{**service, "open_incidents": open_by_service.get(service["id"], [])} for service in services]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=os.getenv("PLATFORM_URL", "http://127.0.0.1:8765"))
    parser.add_argument("--output", help="write report JSON")
    args = parser.parse_args()
    token = os.getenv("PLATFORM_TOKEN")
    if not token: parser.exit(1, "CONFIG ERROR: export PLATFORM_TOKEN=training-token\n")
    with requests.Session() as session:
        session.headers.update({"Authorization": f"Bearer {token}"})
        try:
            rows = collect(session, args.url.rstrip("/"))
        except (requests.RequestException, ValueError, KeyError) as exc:
            parser.exit(1, f"API ERROR: {exc}\n")
    for r in rows:
        print(f"{r['id']:<22} {r['status']:<10} {r['latency_ms']:>4}ms  incidents={','.join(r['open_incidents']) or '-'}")
    print(f"Total: {len(rows)} | Attention: {sum(r['status'] != 'healthy' for r in rows)}")
    if args.output:
        with open(args.output, "w") as f: json.dump(rows, f, indent=2)
    return 2 if any(r['status'] != 'healthy' for r in rows) else 0

if __name__ == "__main__":
    raise SystemExit(main())

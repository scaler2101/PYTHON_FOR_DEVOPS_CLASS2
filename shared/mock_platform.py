#!/usr/bin/env python3
"""Local platform API: paginated service list, incidents, auth, flaky endpoint."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

SERVICES = [
    {"id": "checkout-api", "team": "commerce", "region": "ap-south-1", "status": "healthy", "latency_ms": 92},
    {"id": "payments-api", "team": "payments", "region": "ap-south-1", "status": "degraded", "latency_ms": 960},
    {"id": "catalog-api", "team": "commerce", "region": "eu-west-1", "status": "healthy", "latency_ms": 74},
    {"id": "notification-worker", "team": "platform", "region": "ap-south-1", "status": "unhealthy", "latency_ms": 0},
    {"id": "identity-api", "team": "security", "region": "us-east-1", "status": "healthy", "latency_ms": 112},
]
INCIDENTS = [
    {"id": "INC-241", "service_id": "payments-api", "severity": "high", "state": "open", "summary": "Elevated upstream latency"},
    {"id": "INC-242", "service_id": "notification-worker", "severity": "critical", "state": "open", "summary": "Queue consumer repeatedly exits"},
    {"id": "INC-230", "service_id": "checkout-api", "severity": "low", "state": "resolved", "summary": "Slow responses last week"},
]

class Handler(BaseHTTPRequestHandler):
    attempts = 0

    def send_json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/healthz":
            return self.send_json(200, {"status": "ok", "system": "mock-platform"})
        if self.headers.get("Authorization") != "Bearer training-token":
            return self.send_json(401, {"error": "invalid or missing bearer token"})
        if url.path == "/api/v1/services":
            query = parse_qs(url.query)
            try:
                page = int(query.get("page", ["1"])[0])
                limit = int(query.get("limit", ["2"])[0])
                if page < 1 or limit < 1 or limit > 20: raise ValueError()
            except ValueError:
                return self.send_json(400, {"error": "bad page or limit"})
            offset = (page - 1) * limit
            return self.send_json(200, {"items": SERVICES[offset:offset+limit],
                "page": page, "next_page": page+1 if offset+limit < len(SERVICES) else None})
        if url.path == "/api/v1/incidents":
            return self.send_json(200, {"items": INCIDENTS})
        if url.path == "/api/v1/flaky":
            Handler.attempts += 1
            if Handler.attempts % 3 != 0:
                return self.send_json(503, {"error": "temporary upstream failure"})
            return self.send_json(200, {"status": "recovered", "attempt": Handler.attempts})
        return self.send_json(404, {"error": "unknown endpoint"})

    def log_message(self, fmt, *args):
        print(f"API {self.address_string()} - {fmt % args}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Mock platform running at http://{args.host}:{args.port} (Ctrl-C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()

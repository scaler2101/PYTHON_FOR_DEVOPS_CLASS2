#!/usr/bin/env python3
"""Audit an inventory snapshot. Exit 2 means policy violations were found."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path


def audit(servers):
    counts = Counter(server.get("environment", "unknown") for server in servers)
    ip_counts = Counter(server.get("ip") for server in servers if server.get("ip"))
    findings = []
    for server in servers:
        name = server.get("name", "<unnamed>")
        checks = []
        if not server.get("owner"):
            checks.append("missing_owner")
        if server.get("ip") and ip_counts[server["ip"]] > 1:
            checks.append("duplicate_ip")
        if server.get("environment") == "production":
            if server.get("cpu", 0) < 2 or server.get("memory_gb", 0) < 8:
                checks.append("underprovisioned_production")
            if server.get("backup_enabled") is not True:
                checks.append("backup_disabled")
            if server.get("monitoring_enabled") is not True:
                checks.append("monitoring_disabled")
        findings.extend({"server": name, "rule": rule} for rule in checks)
    return {"total_servers": len(servers), "by_environment": dict(sorted(counts.items())),
            "findings": findings, "violation_count": len(findings)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=Path("data/inventory.json"))
    parser.add_argument("--output", type=Path, help="write the same report as JSON")
    args = parser.parse_args()
    try:
        payload = json.loads(args.inventory.read_text())
        servers = payload["servers"]
        if not isinstance(servers, list):
            raise ValueError("servers must be a list")
        report = audit(servers)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"INPUT ERROR: {exc}\n")
    print(f"Servers: {report['total_servers']} | Violations: {report['violation_count']}")
    print("By environment:", report["by_environment"])
    for finding in report["findings"]:
        print(f"  {finding['server']:<20} {finding['rule']}")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    return 2 if report["violation_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env bash
# jq is doing the JSON parsing here; shell orchestrates the report.
set -euo pipefail
input="${1:-data/inventory.json}"
if [[ ! -f "$input" ]]; then echo "INPUT ERROR: $input not found" >&2; exit 1; fi
# A single jq program expresses the rules correctly, including null/missing fields.
report=$(jq -e '
  .servers as $servers
  | if ($servers | type) != "array" then error("servers must be an array") else . end
  | ($servers | map(.ip // empty) | group_by(.) | map(select(length > 1) | .[0])) as $duplicates
  | [ $servers[] as $s
      | ([ if ($s.owner // "") == "" then "missing_owner" else empty end,
           if (($s.ip // "") != "" and (($duplicates | index($s.ip)) != null)) then "duplicate_ip" else empty end,
           if $s.environment == "production" and (($s.cpu // 0) < 2 or ($s.memory_gb // 0) < 8) then "underprovisioned_production" else empty end,
           if $s.environment == "production" and $s.backup_enabled != true then "backup_disabled" else empty end,
           if $s.environment == "production" and $s.monitoring_enabled != true then "monitoring_disabled" else empty end
         ])[] as $rule
        | {server: ($s.name // "<unnamed>"), rule: $rule} ] as $findings
  | {total_servers: ($servers | length),
     by_environment: ($servers | group_by(.environment // "unknown") | map({key: (.[0].environment // "unknown"), value: length}) | from_entries),
     findings: $findings, violation_count: ($findings | length)}
' "$input") || { echo 'INPUT ERROR: invalid inventory' >&2; exit 1; }
printf '%s\n' "$report" | jq -r '"Servers: \(.total_servers) | Violations: \(.violation_count)", "By environment: \(.by_environment)", (.findings[] | "  \(.server)  \(.rule)")'
if [[ -n "${OUTPUT_JSON:-}" ]]; then printf '%s\n' "$report" > "$OUTPUT_JSON"; fi
violations=$(jq -r '.violation_count' <<< "$report")
if (( violations > 0 )); then exit 2; fi

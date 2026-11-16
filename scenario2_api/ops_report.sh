#!/usr/bin/env bash
# Bash can absolutely do this; curl handles HTTP and jq handles JSON.
set -euo pipefail
base="${PLATFORM_URL:-http://127.0.0.1:8765}"
token="${PLATFORM_TOKEN:?export PLATFORM_TOKEN=training-token first}"
workdir=$(mktemp -d)
trap 'rm -rf "$workdir"' EXIT
api_get() {
  local path="$1" output="$2" attempt status
  for attempt in 1 2 3; do
    status=$(curl --silent --show-error --max-time 2 --output "$output" --write-out '%{http_code}' \
      -H "Authorization: Bearer $token" "$base$path") || status="000"
    case "$status" in
      200) return 0 ;;
      429|500|502|503|504|000) if (( attempt < 3 )); then sleep "0.$((2*attempt))"; continue; fi ;;
    esac
    echo "API ERROR: request $path failed with HTTP $status" >&2
    return 1
  done
}
page=1
printf '[]' > "$workdir/all.json"
while :; do
  api_get "/api/v1/services?page=$page&limit=2" "$workdir/page.json"
  jq -s '.[0] + .[1].items' "$workdir/all.json" "$workdir/page.json" > "$workdir/next.json"
  mv "$workdir/next.json" "$workdir/all.json"
  next_page=$(jq -r '.next_page // empty' "$workdir/page.json")
  [[ -z "$next_page" ]] && break
  if (( next_page <= page )); then echo 'API ERROR: pagination did not advance' >&2; exit 1; fi
  page="$next_page"
done
api_get '/api/v1/incidents' "$workdir/incidents.json"
jq -n --slurpfile services "$workdir/all.json" --slurpfile incidents "$workdir/incidents.json" '
  [ $services[0][] as $s
    | $s + {open_incidents: [$incidents[0].items[] | select(.state == "open" and .service_id == $s.id) | .id]} ]
' > "$workdir/report.json"
jq -r '.[] | "\(.id)\t\(.status)\t\(.latency_ms)ms\tincidents=\(.open_incidents | join(","))"' "$workdir/report.json"
jq -r '"Total: \(length) | Attention: \([.[] | select(.status != "healthy")] | length)"' "$workdir/report.json"
if [[ -n "${OUTPUT_JSON:-}" ]]; then cp "$workdir/report.json" "$OUTPUT_JSON"; fi
attention=$(jq '[.[] | select(.status != "healthy")] | length' "$workdir/report.json")
if (( attention > 0 )); then exit 2; fi

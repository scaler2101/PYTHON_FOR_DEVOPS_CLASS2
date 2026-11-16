#!/usr/bin/env bash
# Streaming awk is often extremely good for this particular kind of log processing.
# Requires GNU awk (gawk) for mktime UTC conversion. Keep all sample timestamps UTC.
set -euo pipefail
log_dir="${1:-data/logs}"
window="${WINDOW_SECONDS:-120}"
threshold="${THRESHOLD:-3}"
[[ -d "$log_dir" && "$window" =~ ^[1-9][0-9]*$ && "$threshold" =~ ^[1-9][0-9]*$ ]] || { echo 'INPUT ERROR' >&2; exit 1; }
shopt -s nullglob
files=("$log_dir"/*.log)
(( ${#files[@]} > 0 )) || { echo 'INPUT ERROR: no log files' >&2; exit 1; }
# Use Python's coreutils equivalent `date`? Here awk scans timestamp sortable strings
# and seconds-from-midnight. Demo dataset stays within a single UTC day.
awk -v window="$window" -v threshold="$threshold" '
  /^20[0-9][0-9]-/ {
    time=substr($1,12,8); split(time,t,":"); seconds=t[1]*3600+t[2]*60+t[3]
    level=""; service=""; code=""
    for (i=2;i<=NF;i++) {
      if ($i ~ /^level=/) {split($i,x,"=");level=x[2]}
      if ($i ~ /^service=/) {split($i,x,"=");service=x[2]}
      if ($i ~ /^code=/) {split($i,x,"=");code=x[2]}
    }
    if (level == "" || service == "" || code == "") { skipped++; next }
    parsed++
    if (level == "ERROR") {
      key=service SUBSEP code; count[key]++
      times[key]=times[key] " " seconds
    }
    next
  }
  {skipped++}
  END {
    printf "Parsed: %d | Skipped: %d\n", parsed, skipped
    for (key in count) {split(key,parts,SUBSEP);printf "%s %s errors=%d\n",parts[1],parts[2],count[key]}
    for (key in times) {
      # sort order is an explicit assumption: example files are read in time order.
      n=split(substr(times[key],2),st," ")
      for (i=1;i<=n;i++) {
        j=i
        while (j>1 && st[i]-st[j-1] <= window) j--
        if (i-j+1>=threshold) {split(key,parts,SUBSEP);printf "ALERT burst %s/%s: >= %d in %ds\n",parts[1],parts[2],i-j+1,window; alerts++;break}
      }
    }
    if (alerts>0) exit 2
  }
' "${files[@]}"

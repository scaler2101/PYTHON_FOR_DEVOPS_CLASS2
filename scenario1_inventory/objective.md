## Requirements
- Count all servers and group them by environment.
- Flag servers with a missing or empty owner (`missing_owner`).
- Flag each server using a duplicated nonempty IP (`duplicate_ip`). For this exercise, IP uniqueness is checked across the entire inventory.
- For **production** servers only, flag CPU below 2 **or** memory below 8 GB (`underprovisioned_production`), backups not explicitly enabled (`backup_disabled`), and monitoring not explicitly enabled (`monitoring_disabled`).
- A server can produce more than one finding.
- Generate a readable terminal summary, and support exporting a machine-readable JSON report.

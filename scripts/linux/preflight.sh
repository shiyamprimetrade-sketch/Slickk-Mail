#!/usr/bin/env bash
# Read only, no DNS/firewall changes.
set -euo pipefail
printf '%s\n' 'SLICKK Mail - production VPS preflight (read-only)'
uname -sm
df -h /
free -h | head -3 || true
if [ -d /cow ]; then echo 'FAIL: live USB /cow detected; do not deploy mail production here'; exit 2; fi
if command -v docker >/dev/null; then docker --version; docker compose version; else echo 'Docker missing'; fi
printf '\nExisting DNS (not modified):\n'
if command -v dig >/dev/null; then
 dig +short MX slickk.online || true
 dig +short A mail.slickk.online || true
 dig +short TXT _dmarc.slickk.online || true
else echo 'Install dnsutils to query existing DNS'; fi
printf '\nProvider must CONFIRM static IPv4, TCP 25 in/out, PTR control, adequate storage, firewall and backups.\n'

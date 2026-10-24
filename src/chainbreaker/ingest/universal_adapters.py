from __future__ import annotations

import csv
import io
import json
import re
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def parse_universal_log(content: str) -> list[dict[str, object]]:
    """Universal parser that auto-detects real-world log dialects:
    1. Zeek TSV logs (dns.log, conn.log)
    2. Linux Auth Syslog (sshd, pam, openvpn in /var/log/auth.log)
    3. Suricata / Zeek EVE JSON
    4. Standard CSV / JSONL
    """
    stripped = content.strip()
    if not stripped:
        return []

    # 1. Zeek TSV log detection
    if "#fields" in stripped or "#separator" in stripped:
        return _parse_zeek_tsv(stripped)

    # 2. Linux Syslog line detection
    first_line = stripped.split("\n", 1)[0]
    if re.match(r"^[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2}", first_line):
        return _parse_syslog(stripped)

    # 3. JSON Lines or JSON Array
    if stripped.startswith("{") or stripped.startswith("["):
        return _parse_json_logs(stripped)

    # 4. Standard CSV
    return _parse_csv_logs(stripped)


def _parse_zeek_tsv(text: str) -> list[dict[str, object]]:
    rows = []
    fields = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#close"):
            continue
        if line.startswith("#fields"):
            fields = line.split()[1:]
            continue
        if line.startswith("#"):
            continue
        if not fields:
            continue
        parts = line.split("\t")
        if len(parts) != len(fields):
            continue
        record = dict(zip(fields, parts))
        
        # Normalize Zeek timestamp
        ts_raw = record.get("ts", "0")
        try:
            ts_float = float(ts_raw)
            dt = datetime.fromtimestamp(ts_float, tz=timezone.utc)
        except Exception:
            dt = datetime.now(timezone.utc)

        rows.append({
            "event_id": f"zeek-{record.get('uid', uuid4().hex[:8])}",
            "row_id": f"zeek-row-{len(rows)+1}",
            "timestamp": dt.isoformat(),
            "source": "dns" if "query" in record else "network",
            "event_type": "dns_query" if "query" in record else "conn",
            "ip": record.get("id.orig_h") or record.get("orig_h"),
            "host": record.get("id.resp_h") or record.get("resp_h"),
            "domain": record.get("query"),
            "success": "true" if record.get("rcode_name") in ("NOERROR", "-") else "false",
        })
    return rows


def _parse_syslog(text: str) -> list[dict[str, object]]:
    rows = []
    current_year = datetime.now(timezone.utc).year
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Example: Oct 24 02:10:00 sso-gateway sshd[1024]: Failed password for invalid user ops_k from 10.20.0.8 port 48291
        match = re.match(
            r"^([A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+([\w\.\-]+)\s+([\w\.\-]+)(?:\[\d+\])?:\s+(.*)$",
            line,
        )
        if not match:
            continue
        ts_str, host, service, msg = match.groups()
        try:
            dt = datetime.strptime(f"{current_year} {ts_str}", "%Y %b %d %H:%M:%S").replace(tzinfo=timezone.utc)
        except Exception:
            dt = datetime.now(timezone.utc)

        # Detect auth failure / spray
        is_fail = any(w in msg.lower() for w in ("failed password", "authentication failure", "invalid user", "login failed"))
        is_success = any(w in msg.lower() for w in ("accepted password", "session opened", "vpn login success"))
        
        # Extract IP and user
        ip_match = re.search(r"from\s+([\d\.]+)", msg)
        ip = ip_match.group(1) if ip_match else None
        
        user_match = re.search(r"for\s+(?:invalid\s+user\s+)?(\w+)", msg)
        user = user_match.group(1) if user_match else None

        rows.append({
            "event_id": f"syslog-{uuid4().hex[:8]}",
            "row_id": f"syslog-row-{len(rows)+1}",
            "timestamp": dt.isoformat(),
            "source": "vpn" if "vpn" in service.lower() else "auth",
            "event_type": "login_failure" if is_fail else ("login_success" if is_success else "syslog_event"),
            "account": user,
            "ip": ip,
            "host": host,
            "success": "true" if is_success else ("false" if is_fail else "unknown"),
        })
    return rows


def _parse_json_logs(text: str) -> list[dict[str, object]]:
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return [dict(item) for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            return [data]
    except Exception:
        pass
    # Try JSONL
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def _parse_csv_logs(text: str) -> list[dict[str, object]]:
    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader]

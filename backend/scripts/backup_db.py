#!/usr/bin/env python3
"""
A.L.F.I.E PostgreSQL Backup Utility.
Executes a compressed pg_dump archive and enforces rolling retention.
"""
import os
import sys
import subprocess
import argparse
from datetime import datetime, timezone
from urllib.parse import urlparse

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings


def parse_dsn(dsn: str):
    """Extract connection parameters from PostgreSQL DSN."""
    parsed = urlparse(dsn)
    return {
        "host": parsed.hostname or "localhost",
        "port": str(parsed.port or 5432),
        "user": parsed.username or "postgres",
        "password": parsed.password or "",
        "database": parsed.path.lstrip("/") or "alfie_db",
    }


def run_backup(output_dir="backups", tag=None, retention_days=7):
    """Create a compressed database backup."""
    # Resolve project root and backup directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.path.isabs(output_dir):
        backup_path = os.path.join(project_root, output_dir)
    else:
        backup_path = output_dir

    os.makedirs(backup_path, exist_ok=True)

    creds = parse_dsn(settings.telemetry_db_dsn)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    tag_part = f"_{tag}" if tag else ""
    filename = f"alfie_db_{timestamp}{tag_part}.dump"
    filepath = os.path.join(backup_path, filename)

    print(f"[*] Initiating backup of database '{creds['database']}' to '{filepath}'...")

    env = os.environ.copy()
    if creds["password"]:
        env["PGPASSWORD"] = creds["password"]

    cmd = [
        "pg_dump",
        "-h", creds["host"],
        "-p", creds["port"],
        "-U", creds["user"],
        "-d", creds["database"],
        "-Fc",  # Custom archive format (compressed)
        "-f", filepath,
    ]

    try:
        subprocess.run(cmd, env=env, check=True)
        size_bytes = os.path.getsize(filepath)
        size_mb = size_bytes / (1024 * 1024)
        print(f"[+] Backup successfully completed: {filename} ({size_mb:.2f} MB)")
    except FileNotFoundError:
        print("[-] Error: 'pg_dump' command not found. Ensure PostgreSQL client utilities are installed.")
        print("    Alternatively, use Docker: docker compose exec postgres pg_dump ...")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[-] Error executing pg_dump: {e}")
        sys.exit(1)

    # Retention cleanup
    if retention_days > 0:
        now_ts = datetime.now(timezone.utc).timestamp()
        cutoff_seconds = retention_days * 86400
        pruned_count = 0
        for fname in os.listdir(backup_path):
            if fname.endswith(".dump") and fname != filename:
                fpath = os.path.join(backup_path, fname)
                try:
                    if (now_ts - os.path.getmtime(fpath)) > cutoff_seconds:
                        os.remove(fpath)
                        pruned_count += 1
                except Exception as e:
                    print(f"[!] Warning: failed to prune old backup {fname}: {e}")

        if pruned_count > 0:
            print(f"[*] Pruned {pruned_count} backup(s) older than {retention_days} days.")

    return filepath


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a PostgreSQL database backup.")
    parser.add_argument("--dir", default="backups", help="Target backup directory (default: backups)")
    parser.add_argument("--tag", default=None, help="Optional tag label in the backup filename")
    parser.add_argument("--retention", type=int, default=7, help="Days to retain old backups (default: 7)")
    args = parser.parse_args()

    run_backup(output_dir=args.dir, tag=args.tag, retention_days=args.retention)

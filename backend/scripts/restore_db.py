#!/usr/bin/env python3
"""
A.L.F.I.E PostgreSQL Restore Utility.
Restores a compressed pg_dump archive into the configured PostgreSQL database.
"""
import os
import sys
import subprocess
import argparse
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


def run_restore(dump_file: str, clean=False, yes=False):
    """Restore a database backup archive."""
    if not os.path.exists(dump_file):
        print(f"[-] Error: Backup file not found at '{dump_file}'")
        sys.exit(1)

    creds = parse_dsn(settings.telemetry_db_dsn)
    print(f"[!] TARGET DATABASE: {creds['database']} on {creds['host']}:{creds['port']}")
    print(f"[!] SOURCE DUMP: {dump_file} ({os.path.getsize(dump_file) / (1024*1024):.2f} MB)")

    if not yes:
        confirm = input(f"Are you sure you want to restore into '{creds['database']}'? Existing data may be overwritten. [y/N]: ")
        if confirm.strip().lower() != "y":
            print("Restore aborted by user.")
            sys.exit(0)

    env = os.environ.copy()
    if creds["password"]:
        env["PGPASSWORD"] = creds["password"]

    cmd = [
        "pg_restore",
        "-h", creds["host"],
        "-p", creds["port"],
        "-U", creds["user"],
        "-d", creds["database"],
        "--no-owner",
        "--no-privileges",
    ]

    if clean:
        cmd.append("--clean")

    cmd.append(dump_file)

    try:
        print(f"[*] Executing pg_restore...")
        subprocess.run(cmd, env=env, check=True)
        print(f"[+] Database restore completed successfully!")
    except FileNotFoundError:
        print("[-] Error: 'pg_restore' command not found. Ensure PostgreSQL client utilities are installed.")
        print("    Alternatively, use Docker: docker compose exec postgres pg_restore ...")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[-] pg_restore exited with error code {e.returncode}: {e}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore a PostgreSQL database backup.")
    parser.add_argument("dump_file", help="Path to the .dump file to restore")
    parser.add_argument("--clean", action="store_true", help="Clean (drop) database objects before recreating them")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    run_restore(dump_file=args.dump_file, clean=args.clean, yes=args.yes)

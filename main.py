#!/usr/bin/env python3
"""PostgreSQL connection checker.

This script attempts to connect to a PostgreSQL database using the connection
string provided via the `DATABASE_URL` environment variable (or
`POSTGRES_CONNECTION_STRING`). It will try multiple times before giving up and
returns an exit code indicating the result.

Usage (inside container):
    docker run --rm -e DATABASE_URL="postgres://user:pass@host:port/db" \
       ghcr.io/<owner>/pg-connection-checker:latest

Exit codes:
    0 – Connection successful
    1 – Missing connection string
    2 – Unable to connect after all retries
"""
import os
import sys
import time

import psycopg2  # type: ignore


def check_connection(conn_str: str, timeout: int = 5) -> bool:
    """Attempt a single connection to the database.

    Returns True on success, False on failure.
    """
    try:
        conn = psycopg2.connect(conn_str, connect_timeout=timeout)
        conn.close()
        return True
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Connection attempt failed: {exc}", file=sys.stderr)
        return False


def main() -> None:  # noqa: D401
    """Run the connectivity check with retries."""
    conn_string = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_CONNECTION_STRING")
    if not conn_string:
        print("Neither DATABASE_URL nor POSTGRES_CONNECTION_STRING is set.", file=sys.stderr)
        sys.exit(1)

    retries = int(os.getenv("RETRIES", "3"))
    delay = int(os.getenv("DELAY", "5"))  # seconds between retries

    for attempt in range(1, retries + 1):
        print(f"Attempt {attempt}/{retries} to connect…")
        if check_connection(conn_string):
            print("Successfully connected to PostgreSQL!")
            sys.exit(0)

        if attempt < retries:
            time.sleep(delay)

    print("All attempts to connect failed.", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()

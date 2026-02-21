"""CLI for syncing employee data from Perfect HR."""

from __future__ import annotations

import argparse
import json
import os
import sys

from perfect_hr_integration import PerfectHRClient, PerfectHRConfig, PerfectHRError, normalize_employee


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync employees from Perfect HR")
    parser.add_argument("--since", help="ISO-8601 timestamp to fetch updates since")
    parser.add_argument("--output", help="Optional output file path for JSON payload")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    base_url = os.getenv("PERFECT_HR_BASE_URL")
    token = os.getenv("PERFECT_HR_API_TOKEN")
    if not base_url or not token:
        print(
            "PERFECT_HR_BASE_URL and PERFECT_HR_API_TOKEN must be set",
            file=sys.stderr,
        )
        return 2

    client = PerfectHRClient(PerfectHRConfig(base_url=base_url, api_token=token))

    try:
        records = client.get_employees(since=args.since)
    except PerfectHRError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    normalized = [normalize_employee(record) for record in records]

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(normalized, f, indent=2)
        print(f"Wrote {len(normalized)} employees to {args.output}")
    else:
        print(json.dumps(normalized, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

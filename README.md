# Perfect HR Integration

This repository provides a lightweight integration layer for **Perfect HR**.

## What is included

- `perfect_hr_integration.py`: reusable API client and transformation helpers.
- `sync_perfect_hr.py`: command-line script to fetch employees and optionally export to JSON.
- `tests/test_perfect_hr_integration.py`: unit tests for client behavior and mapping logic.

## Step-by-step integration guide

Follow these steps to wire Perfect HR into your workflow.

### 1) Confirm API access in Perfect HR

Make sure you have:

- a base API URL (for example: `https://api.perfecthr.example`)
- a valid API token with permissions to read employee records

If available, use Perfect HR's API console to verify the `/v1/employees` endpoint is enabled for your tenant.

### 2) Configure environment variables

Set the following variables in your shell, deployment environment, or secrets manager:

- `PERFECT_HR_BASE_URL`
- `PERFECT_HR_API_TOKEN`

Example:

```bash
export PERFECT_HR_BASE_URL="https://api.perfecthr.example"
export PERFECT_HR_API_TOKEN="<your-token>"
```

### 3) Run an initial sync manually

Fetch all employees:

```bash
python sync_perfect_hr.py
```

Fetch only recently changed employees:

```bash
python sync_perfect_hr.py --since 2025-01-01T00:00:00Z
```

Save output to a file:

```bash
python sync_perfect_hr.py --since 2025-01-01T00:00:00Z --output employees.json
```

### 4) Validate normalized output

The integration maps each employee to this shape:

- `external_id`
- `email`
- `first_name`
- `last_name`
- `department`
- `title`
- `manager_external_id`
- `employment_status`
- `start_date`

Use this stable shape in downstream ETL, HRIS sync jobs, and identity provisioning flows.

### 5) Embed in your own code (optional)

If you want to call the client directly:

```python
from perfect_hr_integration import PerfectHRClient, PerfectHRConfig, normalize_employee

client = PerfectHRClient(
    PerfectHRConfig(
        base_url="https://api.perfecthr.example",
        api_token="<your-token>",
    )
)

raw_records = client.get_employees(since="2025-01-01T00:00:00Z")
normalized = [normalize_employee(record) for record in raw_records]
print(normalized)
```

### 6) Automate recurring syncs

Run `sync_perfect_hr.py` on a schedule (cron, CI, or workflow engine), and persist the last successful `--since` watermark for incremental pulls.

### 7) Add operational safeguards

Recommended production checks:

- monitor job success/failure and alert on repeated `PerfectHRError`
- log API status codes and payload anomalies
- retry transient network errors at the scheduler level
- archive raw exports for audit/debug purposes

## Troubleshooting

- Missing configuration: if env vars are not set, the CLI exits with status `2`.
- Invalid timestamp: if `--since` is not valid ISO-8601, the client raises `PerfectHRError`.
- API/network issue: request failures are surfaced as `PerfectHRError` with context.

## Development

Run tests:

```bash
python -m unittest discover -s tests
```

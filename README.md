# Perfect HR Integration

This repository provides a lightweight integration layer for **Perfect HR**.

## What is included

- `perfect_hr_integration.py`: reusable API client and transformation helpers.
- `sync_perfect_hr.py`: command-line script to fetch employees and optionally export to JSON.
- `tests/test_perfect_hr_integration.py`: unit tests for client behavior and mapping logic.

## Configuration

Set the following environment variables:

- `PERFECT_HR_BASE_URL` (for example, `https://api.perfecthr.example`)
- `PERFECT_HR_API_TOKEN`

## Usage

```bash
python sync_perfect_hr.py --since 2025-01-01T00:00:00Z --output employees.json
```

If `--output` is omitted, normalized employee data is printed to stdout.

## Development

Run tests:

```bash
python -m unittest discover -s tests
```

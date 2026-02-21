"""Perfect HR integration helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
import json
from urllib import error, parse, request


class PerfectHRError(RuntimeError):
    """Raised when Perfect HR API operations fail."""


@dataclass
class PerfectHRConfig:
    base_url: str
    api_token: str
    timeout_seconds: int = 20


class PerfectHRClient:
    def __init__(self, config: PerfectHRConfig) -> None:
        self._config = config

    def get_employees(self, since: str | None = None) -> list[dict[str, Any]]:
        query: dict[str, str] = {}
        if since:
            _validate_iso8601(since)
            query["updated_since"] = since

        endpoint = f"{self._config.base_url.rstrip('/')}/v1/employees"
        if query:
            endpoint = f"{endpoint}?{parse.urlencode(query)}"

        req = request.Request(
            endpoint,
            headers={
                "Authorization": f"Bearer {self._config.api_token}",
                "Accept": "application/json",
            },
            method="GET",
        )

        try:
            with request.urlopen(req, timeout=self._config.timeout_seconds) as resp:
                body = resp.read().decode("utf-8")
                status = getattr(resp, "status", 200)
        except error.URLError as exc:
            raise PerfectHRError(f"Unable to reach Perfect HR: {exc}") from exc

        if status >= 400:
            raise PerfectHRError(f"Perfect HR returned {status}: {body.strip()}")

        payload = json.loads(body)
        employees = payload.get("employees", [])
        if not isinstance(employees, list):
            raise PerfectHRError("Unexpected payload shape: employees must be a list")

        return employees


def normalize_employee(record: dict[str, Any]) -> dict[str, Any]:
    """Map a Perfect HR employee payload to a normalized internal format."""

    return {
        "external_id": record.get("id"),
        "email": record.get("work_email") or record.get("personal_email"),
        "first_name": record.get("first_name"),
        "last_name": record.get("last_name"),
        "department": _nested(record, "org", "department", "name"),
        "title": _nested(record, "job", "title"),
        "manager_external_id": _nested(record, "manager", "id"),
        "employment_status": record.get("status"),
        "start_date": record.get("start_date"),
    }


def _nested(data: dict[str, Any], *path: str) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _validate_iso8601(value: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PerfectHRError(f"Invalid ISO-8601 timestamp: {value}") from exc

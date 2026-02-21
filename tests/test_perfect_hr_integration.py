import json
import unittest
from unittest.mock import patch

from perfect_hr_integration import (
    PerfectHRClient,
    PerfectHRConfig,
    PerfectHRError,
    normalize_employee,
)


class FakeResponse:
    def __init__(self, payload: dict, status: int = 200) -> None:
        self._payload = payload
        self.status = status

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class TestPerfectHRIntegration(unittest.TestCase):
    def test_normalize_employee(self) -> None:
        src = {
            "id": "emp-123",
            "work_email": "person@example.com",
            "first_name": "Ada",
            "last_name": "Lovelace",
            "org": {"department": {"name": "Engineering"}},
            "job": {"title": "Staff Engineer"},
            "manager": {"id": "emp-001"},
            "status": "active",
            "start_date": "2023-04-01",
        }

        out = normalize_employee(src)
        self.assertEqual(out["external_id"], "emp-123")
        self.assertEqual(out["department"], "Engineering")
        self.assertEqual(out["manager_external_id"], "emp-001")

    @patch("perfect_hr_integration.request.urlopen")
    def test_get_employees_success(self, mock_urlopen) -> None:
        mock_urlopen.return_value = FakeResponse({"employees": [{"id": "e1"}]})

        client = PerfectHRClient(
            PerfectHRConfig(base_url="https://api.perfecthr.example", api_token="x")
        )
        employees = client.get_employees(since="2025-01-01T00:00:00Z")

        self.assertEqual(employees, [{"id": "e1"}])
        self.assertIn("updated_since=2025-01-01T00%3A00%3A00Z", mock_urlopen.call_args[0][0].full_url)

    def test_get_employees_validates_since(self) -> None:
        client = PerfectHRClient(
            PerfectHRConfig(base_url="https://api.perfecthr.example", api_token="x")
        )
        with self.assertRaises(PerfectHRError):
            client.get_employees(since="not-a-date")


if __name__ == "__main__":
    unittest.main()

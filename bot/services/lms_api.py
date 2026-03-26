from __future__ import annotations

from typing import Any

import httpx


class BackendError(Exception):
    pass


class LmsApiClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    def _format_error(self, exc: Exception) -> str:
        if isinstance(exc, httpx.HTTPStatusError):
            return f"HTTP {exc.response.status_code} {exc.response.reason_phrase}"
        if isinstance(exc, httpx.ConnectError):
            return f"connection refused ({self.base_url})"
        if isinstance(exc, httpx.TimeoutException):
            return f"request timeout ({self.base_url})"
        return str(exc)

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self._headers(), params=params)
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            raise BackendError(self._format_error(exc)) from exc

    def _post(self, path: str, json_body: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=self._headers(), json=json_body or {})
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            raise BackendError(self._format_error(exc)) from exc

    def get_items(self) -> Any:
        return self._get("/items/")

    def get_learners(self) -> Any:
        return self._get("/learners/")

    def get_scores(self, lab: str) -> Any:
        return self._get("/analytics/scores", params={"lab": lab})

    def get_pass_rates(self, lab: str) -> Any:
        return self._get("/analytics/pass-rates", params={"lab": lab})

    def get_timeline(self, lab: str) -> Any:
        return self._get("/analytics/timeline", params={"lab": lab})

    def get_groups(self, lab: str) -> Any:
        return self._get("/analytics/groups", params={"lab": lab})

    def get_top_learners(self, lab: str | None = None, limit: int = 5) -> Any:
        params: dict[str, Any] = {"limit": limit}
        if lab:
            params["lab"] = lab
        return self._get("/analytics/top-learners", params=params)

    def get_completion_rate(self, lab: str) -> Any:
        return self._get("/analytics/completion-rate", params={"lab": lab})

    def trigger_sync(self) -> Any:
        return self._post("/pipeline/sync", {})

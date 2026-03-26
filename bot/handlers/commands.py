from __future__ import annotations

from typing import Any

from config import get_settings
from services.llm_router import route_natural_language
from services.lms_api import BackendError, LmsApiClient


def _client() -> LmsApiClient:
    settings = get_settings()
    return LmsApiClient(
        base_url=settings.lms_api_base_url,
        api_key=settings.lms_api_key,
    )


def _as_list(data: Any) -> list[Any]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("data", "items", "results", "tasks", "labs", "learners"):
            value = data.get(key)
            if isinstance(value, list):
                return value
        return [data]
    return []


def _format_percent(value: Any) -> str:
    if isinstance(value, (int, float)):
        number = float(value)
        if 0 <= number <= 1:
            number *= 100
        return f"{number:.1f}%"
    return "N/A"


def handle_start() -> str:
    return "Welcome to the LMS bot.\nUse /help to see available commands."

def handle_help() -> str:
    return (
        "Available commands:\n"
        "/start - show welcome message\n"
        "/help - show this help\n"
        "/health - check backend status\n"
        "/labs - list available labs\n"
        "/scores <lab> - show per-task pass rates\n"
        "\nYou can also ask plain questions like:\n"
        "- what labs are available?\n"
        "- who are the top 5 students?\n"
        "- which lab has the lowest pass rate?"
    )

def handle_health() -> str:
    try:
        items = _as_list(_client().get_items())
        return f"Backend is healthy. {len(items)} items available."
    except BackendError as exc:
        return f"Backend error: {exc}. Check that the services are running."

def handle_labs() -> str:
    try:
        items = _as_list(_client().get_items())
        labs = [item for item in items if isinstance(item, dict) and item.get("type") == "lab"]
        if not labs:
            return "No labs found."
        lines = ["Available labs:"]
        for lab in labs:
            lines.append(f"- {lab.get('title', 'Untitled lab')}")
        return "\n".join(lines)
    except BackendError as exc:
        return f"Backend error: {exc}. Check that the services are running."

def handle_scores(argument: str | None = None) -> str:
    if not argument:
        return "Usage: /scores <lab>"
    try:
        rows = _as_list(_client().get_pass_rates(argument))
        if not rows:
            return f"No pass-rate data found for {argument}."
        lines = [f"Pass rates for {argument}:"]
        found_any = False
        for row in rows:
            if not isinstance(row, dict):
                continue
            task_name = (
                row.get("task")
                or row.get("task_title")
                or row.get("title")
                or row.get("name")
                or "Unknown task"
            )
            percent = (
                row.get("pass_rate")
                or row.get("avg_score_pct")
                or row.get("percentage")
                or row.get("avg_percent")
                or row.get("score")
            )
            attempts = (
                row.get("attempts")
                or row.get("submission_count")
                or row.get("count")
                or row.get("n")
            )
            line = f"- {task_name}: {_format_percent(percent)}"
            if attempts is not None:
                line += f" ({attempts} attempts)"
            lines.append(line)
            found_any = True
        if not found_any:
            return f"No pass-rate data found for {argument}."
        return "\n".join(lines)
    except BackendError as exc:
        return f"Backend error: {exc}. Check that the services are running."

def handle_unknown(command: str) -> str:
    return f"Unknown command: {command}. Try /help."

def dispatch_command(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return "Empty input. Try /help."

    parts = raw.split(maxsplit=1)
    command = parts[0]
    argument = parts[1] if len(parts) > 1 else None

    if command == "/start":
        return handle_start()
    if command == "/help":
        return handle_help()
    if command == "/health":
        return handle_health()
    if command == "/labs":
        return handle_labs()
    if command == "/scores":
        return handle_scores(argument)

    return handle_unknown(command)

def dispatch_input(text: str) -> str:
    raw = (text or "").strip()
    if raw.startswith("/"):
        return dispatch_command(raw)
    return route_natural_language(raw)

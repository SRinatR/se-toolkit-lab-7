from __future__ import annotations

import json
import sys
from typing import Any

import httpx

from config import get_settings
from services.lms_api import BackendError, LmsApiClient

SYSTEM_PROMPT = """You are an LMS analytics bot.
You answer questions about labs, tasks, scores, pass rates, groups, learners, timelines, and completion.
Rules:
- If the user asks for LMS data, you MUST use tools.
- Never invent numbers.
- For greetings or gibberish, answer briefly and explain what data you can provide.
- If a question is ambiguous, ask a short clarifying question.
- After tool results arrive, use the real data in your final answer.
- Prefer concise answers with actual lab names, task names, numbers, counts, and percentages.
"""

def _client() -> LmsApiClient:
    settings = get_settings()
    return LmsApiClient(
        base_url=settings.lms_api_base_url,
        api_key=settings.lms_api_key,
    )

def tool_schemas() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "List labs and tasks from the LMS backend.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "Get enrolled learners and group information.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_scores",
                "description": "Get score distribution buckets for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab id like lab-04"}
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task averages and attempt counts for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab id like lab-04"}
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submissions per day timeline for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab id like lab-04"}
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group scores and student counts for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab id like lab-03"}
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners overall or for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Optional lab id like lab-04"},
                        "limit": {"type": "integer", "description": "How many learners to return", "default": 5},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate percentage for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab id like lab-04"}
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Refresh LMS analytics data from autochecker.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    ]

def _content_to_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if text:
                    parts.append(str(text))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)

def _chat(messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
    settings = get_settings()
    url = settings.llm_api_base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": settings.llm_api_model,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0.1,
    }
    with httpx.Client(timeout=90.0) as client:
        response = client.post(
            url,
            headers={
                "Authorization": f"Bearer {settings.llm_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        return response.json()

def _run_tool(name: str, args: dict[str, Any]) -> Any:
    client = _client()
    if name == "get_items":
        return client.get_items()
    if name == "get_learners":
        return client.get_learners()
    if name == "get_scores":
        return client.get_scores(args["lab"])
    if name == "get_pass_rates":
        return client.get_pass_rates(args["lab"])
    if name == "get_timeline":
        return client.get_timeline(args["lab"])
    if name == "get_groups":
        return client.get_groups(args["lab"])
    if name == "get_top_learners":
        return client.get_top_learners(args.get("lab"), int(args.get("limit", 5)))
    if name == "get_completion_rate":
        return client.get_completion_rate(args["lab"])
    if name == "trigger_sync":
        return client.trigger_sync()
    return {"error": f"Unknown tool: {name}"}

def route_natural_language(user_text: str) -> str:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]
    tools = tool_schemas()

    for _ in range(8):
        try:
            data = _chat(messages, tools)
        except Exception as exc:
            return f"LLM error: {exc}"

        msg = data["choices"][0]["message"]
        tool_calls = msg.get("tool_calls") or []

        assistant_msg: dict[str, Any] = {
            "role": "assistant",
            "content": msg.get("content") or "",
        }
        if tool_calls:
            assistant_msg["tool_calls"] = tool_calls
        messages.append(assistant_msg)

        if not tool_calls:
            text = _content_to_text(msg.get("content")).strip()
            if text:
                return text
            return "I didn't understand that. I can list labs, scores, learners, groups, completion rates, and pass rates."

        for call in tool_calls:
            name = call["function"]["name"]
            raw_args = call["function"].get("arguments") or "{}"
            try:
                args = json.loads(raw_args)
            except Exception:
                args = {}

            print(f"[tool] LLM called: {name}({json.dumps(args, ensure_ascii=False)})", file=sys.stderr)

            try:
                result = _run_tool(name, args)
            except BackendError as exc:
                result = {"error": str(exc)}
            except Exception as exc:
                result = {"error": str(exc)}

            if isinstance(result, list):
                size = f"{len(result)} items"
            elif isinstance(result, dict):
                size = f"{len(result)} keys"
            else:
                size = "1 result"

            print(f"[tool] Result: {size}", file=sys.stderr)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "name": name,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

        print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)

    return "I couldn't complete that request. Try again."

def handle_start() -> str:
    return (
        "Welcome to the LMS bot scaffold.\n"
        "Use /help to see available commands."
    )


def handle_help() -> str:
    return (
        "Available commands:\n"
        "/start - show welcome message\n"
        "/help - show this help\n"
        "/health - backend status placeholder\n"
        "/labs - lab list placeholder\n"
        "/scores <lab> - scores placeholder"
    )


def handle_health() -> str:
    return "Backend status: not implemented yet."


def handle_labs() -> str:
    return "Labs list: not implemented yet."


def handle_scores(argument: str | None = None) -> str:
    if not argument:
        return "Usage: /scores <lab>"
    return f"Scores for {argument}: not implemented yet."


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

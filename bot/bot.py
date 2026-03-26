import argparse
import asyncio
import sys

from config import get_settings
from handlers.commands import dispatch_command


def run_test_mode(text: str) -> int:
    try:
        _ = get_settings()
        response = dispatch_command(text)
        print(response)
        return 0
    except Exception as exc:
        print(f"Test mode failed: {exc}", file=sys.stderr)
        return 2


async def run_telegram_mode() -> int:
    settings = get_settings()

    if not settings.bot_token:
        print("BOT_TOKEN is missing in ../.env.bot.secret", file=sys.stderr)
        return 1

    from aiogram import Bot, Dispatcher
    from aiogram.filters import Command
    from aiogram.types import Message

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start_handler(message: Message) -> None:
        await message.answer(dispatch_command("/start"))

    @dp.message(Command("help"))
    async def help_handler(message: Message) -> None:
        await message.answer(dispatch_command("/help"))

    @dp.message(Command("health"))
    async def health_handler(message: Message) -> None:
        await message.answer(dispatch_command("/health"))

    @dp.message(Command("labs"))
    async def labs_handler(message: Message) -> None:
        await message.answer(dispatch_command("/labs"))

    @dp.message(Command("scores"))
    async def scores_handler(message: Message) -> None:
        await message.answer(dispatch_command(message.text or "/scores"))

    @dp.message()
    async def fallback_handler(message: Message) -> None:
        await message.answer(dispatch_command(message.text or ""))

    await dp.start_polling(bot)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", help='Run offline test mode, e.g. --test "/health"')
    args = parser.parse_args()

    if args.test is not None:
        return run_test_mode(args.test)

    return asyncio.run(run_telegram_mode())


if __name__ == "__main__":
    raise SystemExit(main())

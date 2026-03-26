import argparse
import asyncio
import sys

from config import get_settings
from handlers.commands import dispatch_input

def run_test_mode(text: str) -> int:
    try:
        _ = get_settings()
        response = dispatch_input(text)
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
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

    def menu_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Labs", callback_data="cmd:/labs"),
                    InlineKeyboardButton(text="Health", callback_data="cmd:/health"),
                ],
                [
                    InlineKeyboardButton(
                        text="Lowest pass rate",
                        callback_data="nl:which lab has the lowest pass rate?",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Top 5 students",
                        callback_data="nl:who are the top 5 students?",
                    )
                ],
            ]
        )

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start_handler(message: Message) -> None:
        await message.answer(dispatch_input("/start"), reply_markup=menu_keyboard())

    @dp.message(Command("help"))
    async def help_handler(message: Message) -> None:
        await message.answer(dispatch_input("/help"), reply_markup=menu_keyboard())

    @dp.callback_query()
    async def callback_handler(callback: CallbackQuery) -> None:
        data = callback.data or ""
        if data.startswith("cmd:"):
            response = dispatch_input(data[4:])
        elif data.startswith("nl:"):
            response = dispatch_input(data[3:])
        else:
            response = "Unknown action."
        await callback.message.answer(response, reply_markup=menu_keyboard())
        await callback.answer()

    @dp.message()
    async def text_handler(message: Message) -> None:
        await message.answer(dispatch_input(message.text or ""), reply_markup=menu_keyboard())

    await dp.start_polling(bot)
    return 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", help='Run offline test mode')
    args = parser.parse_args()

    if args.test is not None:
        return run_test_mode(args.test)

    return asyncio.run(run_telegram_mode())

if __name__ == "__main__":
    raise SystemExit(main())

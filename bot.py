import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

BOT_TOKEN = os.getenv("BOT_TOKEN", "8146086235:AAFltQPui1QuiEZQyJBL7AowRDzFAvwmFvU")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://nalchik-map-production.up.railway.app")
API_URL = os.getenv("API_URL", "https://nalchik-map-production.up.railway.app")  # для check_access

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=MemoryStorage())

@dp.message()
async def handle_message(message: types.Message):
    if message.text == "/start":
        user_id = message.from_user.id
        username = message.from_user.username or "—"

        try:
            response = requests.get(f"{API_URL}/check_access", params={"user_id": user_id})
            access = response.json().get("access", False)
        except:
            access = False

        if access:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🗺 Открыть карту", web_app=WebAppInfo(url=WEBAPP_URL))]
            ])
            await message.answer("Добро пожаловать! Открой карту 👇", reply_markup=kb)
        else:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💳 Оплатить доступ", url="https://t.me/YourPaymentBot")]
            ])
            await message.answer(
                "<b>🔒 Доступ ограничен</b>
                "Для доступа к карте необходимо оформить подписку.",
                reply_markup=kb
            )

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

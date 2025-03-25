
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

BOT_TOKEN = os.getenv("BOT_TOKEN", "8146086235:AAFltQPui1QuiEZQyJBL7AowRDzFAvwmFvU")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://nalchik-map-production.up.railway.app/")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

@dp.message()
async def handle_message(message: types.Message):
    if message.text == "/start":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗺 Открыть карту", web_app=WebAppInfo(url=WEBAPP_URL))]
        ])
        await message.answer("Открой карту ниже 👇", reply_markup=kb)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

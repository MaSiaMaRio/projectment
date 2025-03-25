import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# Получаем токен и URL из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN", "8146086235:AAFltQPui1QuiEZQyJBL7AowRDzFAvwmFvU")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://nalchik-map-production.up.railway.app/")

# Создаём бота с корректной передачей parse_mode
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Диспетчер
dp = Dispatcher(storage=MemoryStorage())

@dp.message()
async def handle_message(message: types.Message):
    if message.text == "/start":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗺 Открыть карту", web_app=WebAppInfo(url=WEBAPP_URL))]
        ])
        await message.answer("Открой карту ниже 👇", reply_markup=kb)

# Запуск бота
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

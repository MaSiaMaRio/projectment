from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "8146086235:AAFltQPui1QuiEZQyJBL7AowRDzFAvwmFvU"
WEBAPP_URL = "https://nalchik-map-production.up.railway.app/"  # твоя ссылка с Railway

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗺 Открыть карту", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await msg.answer("Нажми на кнопку, чтобы открыть карту👇", reply_markup=kb)

if __name__ == "__main__":
    executor.start_polling(dp)

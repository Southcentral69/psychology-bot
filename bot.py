import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import BotCommand
from aiogram import Router
import openai
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Настройка OpenRouter (через openai-библиотеку)
openai.api_key = OPENROUTER_API_KEY
openai.base_url = "https://openrouter.ai/api/v1"

# Промпт — кто ты, как себя вести
SYSTEM_PROMPT = (
    "Ты — заботливый психолог, работающий с детьми. "
    "Ты всегда отвечаешь мягко, понятно и с поддержкой. "
    "Если ребёнок жалуется на насилие, ты предлагаешь безопасные шаги: обратиться к взрослому, доверенному лицу или на горячую линию."
)

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Обработка команды /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! 👋\n"
        "Я здесь, чтобы помочь тебе. Можешь рассказать, что тебя волнует 💬"
    )

# Обработка всех остальных сообщений
@router.message(F.text)
async def handle_message(message: Message):
    user_input = message.text

    try:
        response = openai.ChatCompletion.create(
            model="mistralai/mistral-7b-instruct",  # Можно сменить модель
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
        )

        reply = response['choices'][0]['message']['content']
        await message.answer(reply)

    except Exception as e:
        logging.error(f"Ошибка при запросе к ИИ: {e}")
        await message.answer("⚠️ Ошибка: Не удалось получить ответ от ИИ.")

# Запуск бота
if __name__ == "__main__":
    import asyncio
    async def main():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    asyncio.run(main())

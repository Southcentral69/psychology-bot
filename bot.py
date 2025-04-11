import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from openai import OpenAI

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Проверка токенов
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не установлен!")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY не установлен!")

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Инициализация клиента OpenRouter
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

# Промпт-подсказка — как должен отвечать бот
SYSTEM_PROMPT = (
    "Ты — опытный детский психолог, который разговаривает с ребёнком. "
    "Твоя задача — поддержать его, выслушать, помочь понять и выразить свои чувства. "
    "Отвечай доброжелательно, простыми словами, мягким тоном. Не осуждай. "
    "Если ребёнок говорит о насилии или тревоге — успокой его, объясни, что он не виноват, "
    "и предложи обратиться к взрослому, которому он доверяет (родителю, учителю, психологу)."
)

# Команда /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет, я психолог-бот 🤗\n"
        "Ты можешь рассказать мне, что тебя тревожит, что у тебя на душе.\n"
        "Я выслушаю и постараюсь помочь ❤️"
    )

# Обработка сообщений
@router.message(F.text)
async def handle_message(message: Message):
    user_input = message.text
    thinking = await message.answer("Я думаю… ⏳")

    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content
        await message.answer(reply)
    except Exception as e:
        logging.exception("Ошибка при обращении к OpenRouter")
        await message.answer("⚠️ Прости, я сейчас не смог ответить. Попробуй чуть позже.")
    finally:
        await thinking.delete()

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

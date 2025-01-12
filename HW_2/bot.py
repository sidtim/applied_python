import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import TOKEN
from handlers import daily_norm_calories, logging_activity
from middlewares.middleware import LoggingMiddleware

sys.path.append("..")


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
# Диспетчер
dp = Dispatcher()
# Подключаем middleware
dp.message.middleware(LoggingMiddleware())
# Подключение роутера
dp.include_routers(daily_norm_calories.router, logging_activity.router)


# Запуск процесса полинга новых апдейтов
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from database.connection import init_db
from scheduler.reminder_scheduler import setup_scheduler

# Импортируем все обработчики
from handlers.start import router as start_router
from handlers.quick_note import router as quick_note_router
from handlers.notes_management import router as notes_management_router
from handlers.tags import router as tags_router
from handlers.search import router as search_router
from handlers.reminders import router as reminders_router

async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    

    try:
        init_db()
        logging.info("✅ База данных инициализирована")
    except Exception as e:
        logging.error(f"❌ Ошибка инициализации БД: {e}")
        return
    
    # Создание бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    routers = [
        start_router,
        quick_note_router, 
        notes_management_router,
        tags_router,
        search_router,
        reminders_router
    ]
    
    for router in routers:
        dp.include_router(router)
  
    scheduler = setup_scheduler(bot)
    scheduler.start()
    
    try:
        logging.info("✅ Бот запущен и готов к работе")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"❌ Ошибка при запуске бота: {e}")
    finally:
        scheduler.shutdown()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except(KeyboardInterrupt):
        print("The program is finished!")
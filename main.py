import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, LOG_LEVEL
from database import init_db
from handlers import start, menu, banquet, booking

# Настройка логирования
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

async def main():
    """Главная функция запуска бота"""
    # Инициализация базы данных
    await init_db()
    
    # Создание бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(banquet.router)
    dp.include_router(booking.router)
    
    # Обработчик выбора филиала
    @dp.callback_query(lambda c: c.data.startswith("filial:"))
    async def process_filial_selection(callback: CallbackQuery, state: FSMContext):
        from keyboards.filial import main_menu_keyboard
        from data.filials import get_filial_info
        
        filial_id = callback.data.split(":")[1]
        filial_info = get_filial_info(filial_id)
        
        await state.update_data(filial_id=filial_id)
        
        await callback.message.edit_text(
            f"🍺 <b>{filial_info['name']}</b>\n\n"
            f"📍 {filial_info['address']}\n"
            f"📞 {filial_info['phone']}\n\n"
            f"Выберите действие:",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(filial_info.get("has_delivery", False))
        )
    
    # Запуск бота
    logger.info("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    from aiogram.types import CallbackQuery
    from aiogram.fsm.context import FSMContext
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен!")
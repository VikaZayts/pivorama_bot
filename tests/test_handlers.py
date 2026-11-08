# tests/test_database.py
import pytest
from database import init_db, save_booking

@pytest.mark.asyncio
async def test_init_db():
    """Тест инициализации базы данных"""
    await init_db()
    # Проверка что таблицы созданы

@pytest.mark.asyncio
async def test_save_booking():
    """Тест сохранения бронирования"""
    result = await save_booking(
        user_id=123,
        username="test_user",
        filial_id="nevskiy",
        booking_type="banquet",
        details={"hall": "vip", "guests": 10}
    )
    assert result is not None
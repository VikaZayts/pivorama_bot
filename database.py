import aiosqlite
from datetime import datetime
from config import DATABASE_PATH

async def init_db():
    """Инициализация базы данных"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                filial_id TEXT NOT NULL,
                booking_type TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                filial_id TEXT NOT NULL,
                items TEXT NOT NULL,
                total_price INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def save_booking(user_id: int, username: str, filial_id: str, 
                       booking_type: str, details: dict):
    """Сохранить бронирование"""
    import json
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            INSERT INTO bookings (user_id, username, filial_id, booking_type, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, filial_id, booking_type, json.dumps(details)))
        await db.commit()

async def save_order(user_id: int, username: str, filial_id: str, 
                     items: list, total_price: int):
    """Сохранить заказ"""
    import json
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            INSERT INTO orders (user_id, username, filial_id, items, total_price)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, filial_id, json.dumps(items), total_price))
        await db.commit()
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.menu import MENU_CATEGORIES

def menu_categories_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора категории меню"""
    keyboard = []
    for cat_id, category in MENU_CATEGORIES.items():
        keyboard.append([
            InlineKeyboardButton(
                text=category["name"],
                callback_data=f"menu_cat:{cat_id}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def menu_items_keyboard(category_id: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора блюда из категории"""
    category = MENU_CATEGORIES.get(category_id, {})
    keyboard = []
    
    for item in category.get("items", []):
        keyboard.append([
            InlineKeyboardButton(
                text=f"{item['name']} - {item['price']}₽",
                callback_data=f"add_item:{item['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(text="◀️ К категориям", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def cart_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура корзины"""
    keyboard = [
        [InlineKeyboardButton(text="✅ Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton(text="❌ Очистить корзину", callback_data="clear_cart")],
        [InlineKeyboardButton(text="◀️ Продолжить заказ", callback_data="menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
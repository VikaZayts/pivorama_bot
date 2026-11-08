from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.filials import get_filial_info

def banquet_halls_keyboard(filial_id: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора зала для банкета"""
    filial_info = get_filial_info(filial_id)
    keyboard = []
    
    for hall_id, hall in filial_info.get("halls", {}).items():
        keyboard.append([
            InlineKeyboardButton(
                text=f"{hall['name']} (до {hall['capacity']} чел.)",
                callback_data=f"banquet_hall:{hall_id}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_banquet")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def banquet_menu_keyboard(filial_id: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора банкетного меню"""
    filial_info = get_filial_info(filial_id)
    keyboard = []
    
    for i, menu in enumerate(filial_info.get("banquet_menus", [])):
        emoji = ["🥉", "🥈", "🥇"][i] if i < 3 else "🎊"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{emoji} {menu['price']}₽ - {menu['description']}",
                callback_data=f"banquet_menu:{menu['price']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_banquet")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
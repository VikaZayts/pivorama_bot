from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def delivery_cart_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура корзины доставки"""
    keyboard = [
        [InlineKeyboardButton(text="🚗 Перейти к оформлению", callback_data="delivery:checkout")],
        [InlineKeyboardButton(text="❌ Очистить корзину", callback_data="delivery:clear")],
        [InlineKeyboardButton(text="◀️ Продолжить выбор", callback_data="delivery:continue")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def delivery_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения доставки"""
    keyboard = [
        [InlineKeyboardButton(text="✅ Подтвердить заказ", callback_data="delivery:confirm")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="delivery:cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
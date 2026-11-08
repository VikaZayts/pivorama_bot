from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def filial_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора филиала"""
    keyboard = [
        [InlineKeyboardButton(text="📍 пл. Александра Невского", callback_data="filial:nevskiy")],
        [InlineKeyboardButton(text="📍 Колпино (есть доставка)", callback_data="filial:kolpino")],
        [InlineKeyboardButton(text="📍 Комендантская площадь", callback_data="filial:komendant")],
        [InlineKeyboardButton(text="📍 Белы Куна", callback_data="filial:bely_kuna")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def main_menu_keyboard(has_delivery: bool = False) -> InlineKeyboardMarkup:
    """Главное меню после выбора филиала"""
    keyboard = [
        [InlineKeyboardButton(text="🍽 Меню", callback_data="menu")],
        [InlineKeyboardButton(text="🎉 Забронировать банкет", callback_data="banquet:start")],
        [InlineKeyboardButton(text="🪑 Забронировать столик", callback_data="booking:start")]
    ]
    
    if has_delivery:
        keyboard.append([InlineKeyboardButton(text="🚗 Заказать доставку", callback_data="delivery")])
    
    keyboard.extend([
        [InlineKeyboardButton(text="🎁 Акции", callback_data="promotions")],
        [InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")],
        [InlineKeyboardButton(text="🔄 Сменить филиал", callback_data="change_filial")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
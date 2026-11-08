from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from keyboards.filial import filial_keyboard, main_menu_keyboard
from data.filials import FILIALS, get_filial_info
from data.promotions import get_active_promotions

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    await message.answer(
        "🍺 <b>Добро пожаловать в Пивораму!</b>\n\n"
        "Выберите ресторан:",
        parse_mode="HTML",
        reply_markup=filial_keyboard()
    )


@router.callback_query(F.data == "change_filial")
async def change_filial(callback: CallbackQuery, state: FSMContext):
    """Смена филиала"""
    await callback.answer()
    await state.clear()
    
    await callback.message.edit_text(
        "🍺 <b>Выберите ресторан:</b>",
        parse_mode="HTML",
        reply_markup=filial_keyboard()
    )


@router.callback_query(F.data == "promotions")
async def show_promotions(callback: CallbackQuery, state: FSMContext):
    """Показать активные акции"""
    await callback.answer()
    
    promotions = get_active_promotions()
    
    if not promotions:
        text = "🎁 <b>Акции</b>\n\nК сожалению, сейчас нет активных акций.\nСледите за нашими обновлениями!"
    else:
        text = "🎁 <b>Актуальные акции:</b>\n\n"
        for promo in promotions:
            text += f"• <b>{promo['name']}</b>\n"
            text += f"  {promo['description']}\n"
            if promo.get('discount_percent'):
                text += f"  💰 Скидка: {promo['discount_percent']}%\n"
            text += "\n"
        text += "📍 Выберите филиал для оформления заказа!"
    
    # Получаем текущий филиал для возврата в меню
    data = await state.get_data()
    filial_id = data.get("filial_id")
    filial_info = get_filial_info(filial_id) if filial_id else {}
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_promotions")]
    ])
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "back_to_promotions")
async def back_from_promotions(callback: CallbackQuery, state: FSMContext):
    """Возврат из акций в главное меню"""
    await callback.answer()
    
    data = await state.get_data()
    filial_id = data.get("filial_id")
    filial_info = get_filial_info(filial_id) if filial_id else {}
    
    await callback.message.edit_text(
        f"🍺 <b>{filial_info.get('name', 'Ресторан')}</b>\n\n"
        f"📍 {filial_info.get('address', '')}\n"
        f"📞 {filial_info.get('phone', '')}\n\n"
        f"Выберите действие:",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(filial_info.get("has_delivery", False))
    )


@router.callback_query(F.data == "contacts")
async def show_contacts(callback: CallbackQuery, state: FSMContext):
    """Показать контакты всех филиалов"""
    await callback.answer()
    
    text = "📞 <b>Контакты сети «Пиворама»</b>\n\n"
    
    for filial_id, filial in FILIALS.items():
        text += f"📍 <b>{filial['name']}</b>\n"
        text += f"🏠 Адрес: {filial['address']}\n"
        text += f"☎️ Телефон: {filial['phone']}\n"
        text += "🕐 Часы работы:\n"
        for day, hours in filial['work_hours'].items():
            text += f"   • {day}: {hours}\n"
        if filial.get('has_delivery'):
            text += "   🚗 <i>Доступна доставка</i>\n"
        text += "\n"
    
    text += "Ждём вас в любом из наших ресторанов!"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_contacts")]
    ])
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "back_to_contacts")
async def back_from_contacts(callback: CallbackQuery, state: FSMContext):
    """Возврат из контактов в главное меню"""
    await callback.answer()
    
    data = await state.get_data()
    filial_id = data.get("filial_id")
    filial_info = get_filial_info(filial_id) if filial_id else {}
    
    await callback.message.edit_text(
        f"🍺 <b>{filial_info.get('name', 'Ресторан')}</b>\n\n"
        f"📍 {filial_info.get('address', '')}\n"
        f"📞 {filial_info.get('phone', '')}\n\n"
        f"Выберите действие:",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(filial_info.get("has_delivery", False))
    )
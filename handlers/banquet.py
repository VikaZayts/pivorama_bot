from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.banquet import banquet_halls_keyboard, banquet_menu_keyboard
from keyboards.filial import main_menu_keyboard
from data.filials import get_filial_info
from database import save_booking
from utils.google_sheets import export_booking_to_sheet

router = Router()

class BanquetState(StatesGroup):
    """Состояния бронирования банкета"""
    choosing_hall = State()
    choosing_menu = State()
    entering_guests = State()
    entering_date = State()
    entering_phone = State()
    confirming = State()

@router.callback_query(F.data == "banquet:start")
async def start_banquet_booking(callback: CallbackQuery, state: FSMContext):
    """Начать бронирование банкета"""
    data = await state.get_data()
    filial_id = data.get("filial_id")
    
    await callback.message.edit_text(
        "🎉 <b>Бронирование банкета</b>\n\n"
        "Выберите зал:",
        parse_mode="HTML",
        reply_markup=banquet_halls_keyboard(filial_id)
    )
    await state.set_state(BanquetState.choosing_hall)

@router.callback_query(BanquetState.choosing_hall, F.data.startswith("banquet_hall:"))
async def choose_hall(callback: CallbackQuery, state: FSMContext):
    """Выбор зала"""
    hall_id = callback.data.split(":")[1]
    data = await state.get_data()
    filial_id = data.get("filial_id")
    filial_info = get_filial_info(filial_id)
    
    hall = filial_info.get("halls", {}).get(hall_id, {})
    await state.update_data(hall_id=hall_id, hall_name=hall.get("name"))
    
    await callback.message.edit_text(
        f"🍽 <b>Выберите банкетное меню:</b>\n\n"
        f"Зал: {hall.get('name')}",
        parse_mode="HTML",
        reply_markup=banquet_menu_keyboard(filial_id)
    )
    await state.set_state(BanquetState.choosing_menu)

@router.callback_query(BanquetState.choosing_menu, F.data.startswith("banquet_menu:"))
async def choose_menu(callback: CallbackQuery, state: FSMContext):
    """Выбор меню"""
    menu_price = int(callback.data.split(":")[1])
    await state.update_data(menu_price=menu_price)
    
    await callback.message.edit_text(
        "👥 <b>Сколько будет гостей?</b>\n\n"
        "Введите число:",
        parse_mode="HTML"
    )
    await state.set_state(BanquetState.entering_guests)

@router.message(BanquetState.entering_guests)
async def enter_guests(message: Message, state: FSMContext):
    """Ввод количества гостей"""
    try:
        guests = int(message.text)
        if guests < 1 or guests > 200:
            await message.answer("❌ Введите число от 1 до 200")
            return
        
        await state.update_data(guests=guests)
        await message.answer(
            "📅 <b>На какую дату планируете банкет?</b>\n\n"
            "Введите в формате ДД.ММ.ГГГГ (например, 25.12.2026):",
            parse_mode="HTML"
        )
        await state.set_state(BanquetState.entering_date)
    except ValueError:
        await message.answer("❌ Введите корректное число")

@router.message(BanquetState.entering_date)
async def enter_date(message: Message, state: FSMContext):
    """Ввод даты"""
    await state.update_data(date=message.text)
    await message.answer(
        "📞 <b>Ваш контактный телефон?</b>\n\n"
        "Введите номер:",
        parse_mode="HTML"
    )
    await state.set_state(BanquetState.entering_phone)

@router.message(BanquetState.entering_phone)
async def enter_phone(message: Message, state: FSMContext):
    """Ввод телефона"""
    await state.update_data(phone=message.text)
    
    data = await state.get_data()
    filial_id = data.get("filial_id")
    filial_info = get_filial_info(filial_id)
    
    # Формируем подтверждение
    confirmation_text = (
        "✅ <b>Подтверждение бронирования:</b>\n\n"
        f"📍 Ресторан: {filial_info.get('name')}\n"
        f"🏛 Зал: {data.get('hall_name')}\n"
        f"📅 Дата: {data.get('date')}\n"
        f"👥 Гостей: {data.get('guests')}\n"
        f"🍽 Меню: {data.get('menu_price')}₽/чел\n"
        f"💰 Итого: {data.get('menu_price') * data.get('guests')}₽\n"
        f"📞 Телефон: {data.get('phone')}\n\n"
        f"Всё верно?"
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="banquet:confirm")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="banquet:cancel")]
    ])
    
    await message.answer(confirmation_text, parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(BanquetState.confirming)

@router.callback_query(BanquetState.confirming, F.data == "banquet:confirm")
async def confirm_banquet(callback: CallbackQuery, state: FSMContext):
    """Подтверждение бронирования"""
    data = await state.get_data()
    filial_id = data.get("filial_id")
    filial_info = get_filial_info(filial_id)
    
    booking_details = {
        "type": "Банкет",
        "hall": data.get("hall_name"),
        "date": data.get("date"),
        "guests": data.get("guests"),
        "menu_price": data.get("menu_price"),
        "total_price": data.get("menu_price") * data.get("guests"),
        "phone": data.get("phone")
    }
    
    # Сохраняем в БД
    await save_booking(
        user_id=callback.from_user.id,
        username=callback.from_user.username or callback.from_user.full_name,
        filial_id=filial_id,
        booking_type="banquet",
        details=booking_details
    )
    
    # Экспортируем в Google Sheets
    export_booking_to_sheet({
        "username": callback.from_user.username or callback.from_user.full_name,
        "filial_name": filial_info.get("name"),
        "type": "Банкет",
        "date": data.get("date"),
        "guests": data.get("guests"),
        "details": f"Зал: {data.get('hall_name')}, Меню: {data.get('menu_price')}₽",
        "phone": data.get("phone")
    })
    
    await callback.message.edit_text(
        "✅ <b>Банкет забронирован!</b>\n\n"
        f"Мы свяжемся с вами по номеру {data.get('phone')} для подтверждения.",
        parse_mode="HTML"
    )
    await state.clear()

@router.callback_query(F.data == "cancel_banquet")
async def cancel_banquet(callback: CallbackQuery, state: FSMContext):
    """Отмена бронирования"""
    await state.clear()
    data = await state.get_data()
    filial_id = data.get("filial_id")
    filial_info = get_filial_info(filial_id)
    
    await callback.message.edit_text(
        "❌ Бронирование отменено",
        reply_markup=main_menu_keyboard(filial_info.get("has_delivery", False))
    )
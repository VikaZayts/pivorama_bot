from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.filial import main_menu_keyboard
from data.filials import get_filial_info
from database import save_booking
from utils.google_sheets import export_booking_to_sheet

router = Router()

class TableBookingState(StatesGroup):
    """Состояния для бронирования столика"""
    entering_guests = State()
    entering_date = State()
    entering_phone = State()
    confirming = State()

@router.callback_query(F.data == "booking:start")
async def start_table_booking(callback: CallbackQuery, state: FSMContext):
    """Начать бронирование столика"""
    await callback.answer()  # ✅ Добавлено
    await callback.message.edit_text(
        "🪑 <b>Бронирование столика</b>\n\n"
        "Сколько будет гостей? (Введите число от 1 до 20):",
        parse_mode="HTML"
    )
    await state.set_state(TableBookingState.entering_guests)

@router.message(TableBookingState.entering_guests)
async def enter_guests(message: Message, state: FSMContext):
    """Ввод количества гостей"""
    try:
        guests = int(message.text)
        if guests < 1 or guests > 20:
            await message.answer("❌ Введите число от 1 до 20")
            return
        
        await state.update_data(guests=guests)
        await message.answer(
            "📅 <b>На какую дату и время?</b>\n\n"
            "Введите в формате ДД.ММ.ГГГГ ЧЧ:ММ (например, 25.12.2026 19:00):",
            parse_mode="HTML"
        )
        await state.set_state(TableBookingState.entering_date)
    except ValueError:
        await message.answer("❌ Введите корректное число")

@router.message(TableBookingState.entering_date)
async def enter_date(message: Message, state: FSMContext):
    """Ввод даты и времени"""
    await state.update_data(date=message.text)
    await message.answer(
        "📞 <b>Ваш контактный телефон?</b>\n\n"
        "Введите номер:",
        parse_mode="HTML"
    )
    await state.set_state(TableBookingState.entering_phone)

@router.message(TableBookingState.entering_phone)
async def enter_phone(message: Message, state: FSMContext):
    """Ввод телефона и показ подтверждения"""
    await state.update_data(phone=message.text)
    
    data = await state.get_data()
    filial_id = data.get("filial_id")
    filial_info = get_filial_info(filial_id) if filial_id else {}
    
    confirmation_text = (
        "✅ <b>Подтверждение бронирования столика:</b>\n\n"
        f"📍 Ресторан: {filial_info.get('name', 'Не выбран')}\n"
        f"📅 Дата и время: {data.get('date')}\n"
        f"👥 Гостей: {data.get('guests')}\n"
        f"📞 Телефон: {data.get('phone')}\n\n"
        f"Всё верно?"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="booking:confirm")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="booking:cancel")]
    ])
    
    await message.answer(confirmation_text, parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(TableBookingState.confirming)

@router.callback_query(TableBookingState.confirming, F.data == "booking:confirm")
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    """Подтверждение и сохранение бронирования"""
    await callback.answer()  # ✅ КРИТИЧЕСКИ ВАЖНО!
    
    data = await state.get_data()
    filial_id = data.get("filial_id")
    filial_info = get_filial_info(filial_id) if filial_id else {}
    
    booking_details = {
        "type": "Столик",
        "date": data.get("date"),
        "guests": data.get("guests"),
        "phone": data.get("phone")
    }
    
    # Сохраняем в БД
    await save_booking(
        user_id=callback.from_user.id,
        username=callback.from_user.username or callback.from_user.full_name,
        filial_id=filial_id,
        booking_type="table",
        details=booking_details
    )
    
    # Экспортируем в Google Sheets (если настроено)
    try:
        export_booking_to_sheet({
            "username": callback.from_user.username or callback.from_user.full_name,
            "filial_name": filial_info.get("name", ""),
            "type": "Столик",
            "date": data.get("date"),
            "guests": data.get("guests"),
            "details": f"Гостей: {data.get('guests')}",
            "phone": data.get("phone")
        })
    except Exception as e:
        print(f"Ошибка экспорта в Google Sheets: {e}")
    
    await callback.message.edit_text(
        "✅ <b>Столик забронирован!</b>\n\n"
        f"Мы свяжемся с вами по номеру {data.get('phone')} для подтверждения.",
        parse_mode="HTML"
    )
    await state.clear()

@router.callback_query(F.data == "booking:cancel")
async def cancel_booking(callback: CallbackQuery, state: FSMContext):
    """Отмена бронирования"""
    await callback.answer()  # ✅ Добавлено
    
    data = await state.get_data()
    filial_id = data.get("filial_id")
    await state.clear()
    
    filial_info = get_filial_info(filial_id) if filial_id else {}
    
    await callback.message.edit_text(
        "❌ Бронирование отменено",
        reply_markup=main_menu_keyboard(filial_info.get("has_delivery", False))
    )
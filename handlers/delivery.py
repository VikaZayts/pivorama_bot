from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.filial import main_menu_keyboard
from keyboards.menu import menu_categories_keyboard, menu_items_keyboard
from keyboards.delivery import delivery_cart_keyboard, delivery_confirm_keyboard
from data.filials import get_filial_info
from data.menu import MENU_CATEGORIES, get_item_by_id
from database import save_order
from utils.google_sheets import export_order_to_sheet

router = Router()


class DeliveryState(StatesGroup):
    """Состояния для оформления доставки"""
    viewing_menu = State()
    cart = State()
    entering_address = State()
    entering_phone = State()
    confirming = State()


@router.callback_query(F.data == "delivery")
async def start_delivery(callback: CallbackQuery, state: FSMContext):
    """Начать оформление доставки"""
    await callback.answer()
    
    data = await state.get_data()
    filial_id = data.get("filial_id")
    filial_info = get_filial_info(filial_id)
    
    if not filial_info.get("has_delivery"):
        await callback.message.edit_text(
            "❌ Доставка недоступна в этом филиале",
            reply_markup=main_menu_keyboard(False)
        )
        return
    
    await callback.message.edit_text(
        "🚗 <b>Заказ доставки</b>\n\n"
        "Выберите категорию блюд:",
        parse_mode="HTML",
        reply_markup=menu_categories_keyboard()
    )
    await state.set_state(DeliveryState.viewing_menu)


@router.callback_query(DeliveryState.viewing_menu, F.data.startswith("menu_cat:"))
async def show_category_items(callback: CallbackQuery, state: FSMContext):
    """Показать блюда категории"""
    await callback.answer()
    category_id = callback.data.split(":")[1]
    category = MENU_CATEGORIES.get(category_id, {})
    
    items_text = f"<b>{category['name']}</b>\n\n"
    for item in category.get("items", []):
        items_text += f"• {item['name']} ({item['weight']}) - <b>{item['price']}₽</b>\n"
    
    await callback.message.edit_text(
        items_text,
        parse_mode="HTML",
        reply_markup=menu_items_keyboard(category_id)
    )


@router.callback_query(DeliveryState.viewing_menu, F.data.startswith("add_item:"))
async def add_to_cart(callback: CallbackQuery, state: FSMContext):
    """Добавить блюдо в корзину"""
    item_id = callback.data.split(":")[1]
    item = get_item_by_id(item_id)
    
    if not item:
        await callback.answer("❌ Блюдо не найдено")
        return
    
    data = await state.get_data()
    cart = data.get("cart", [])
    
    existing_item = next((i for i in cart if i["id"] == item_id), None)
    
    if existing_item:
        existing_item["quantity"] += 1
    else:
        cart.append({**item, "quantity": 1})
    
    await state.update_data(cart=cart)
    await callback.answer(f"✅ {item['name']} добавлено в корзину!")


@router.callback_query(DeliveryState.viewing_menu, F.data == "checkout")
async def show_delivery_cart(callback: CallbackQuery, state: FSMContext):
    """Показать корзину доставки"""
    await callback.answer()
    data = await state.get_data()
    cart = data.get("cart", [])
    
    if not cart:
        await callback.answer("🛒 Корзина пуста!")
        return
    
    cart_text = "🛒 <b>Ваш заказ на доставку:</b>\n\n"
    total = 0
    
    for item in cart:
        item_total = item["price"] * item["quantity"]
        total += item_total
        cart_text += f"• {item['name']} × {item['quantity']} = {item_total}₽\n"
    
    cart_text += f"\n💰 <b>Итого: {total}₽</b>"
    
    await state.update_data(total_price=total)
    await callback.message.edit_text(
        cart_text,
        parse_mode="HTML",
        reply_markup=delivery_cart_keyboard()
    )
    await state.set_state(DeliveryState.cart)


@router.callback_query(DeliveryState.cart, F.data == "delivery:clear")
async def clear_delivery_cart(callback: CallbackQuery, state: FSMContext):
    """Очистить корзину доставки"""
    await callback.answer("🗑 Корзина очищена!")
    await state.update_data(cart=[])
    await callback.message.edit_text(
        "🚗 <b>Заказ доставки</b>\n\n"
        "Выберите категорию блюд:",
        parse_mode="HTML",
        reply_markup=menu_categories_keyboard()
    )
    await state.set_state(DeliveryState.viewing_menu)


@router.callback_query(DeliveryState.cart, F.data == "delivery:continue")
async def continue_delivery(callback: CallbackQuery, state: FSMContext):
    """Продолжить выбор блюд"""
    await callback.answer()
    await callback.message.edit_text(
        "🚗 <b>Заказ доставки</b>\n\n"
        "Выберите категорию блюд:",
        parse_mode="HTML",
        reply_markup=menu_categories_keyboard()
    )
    await state.set_state(DeliveryState.viewing_menu)


@router.callback_query(DeliveryState.cart, F.data == "delivery:checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    """Начать оформление - запросить адрес"""
    await callback.answer()
    await callback.message.edit_text(
        "🏠 <b>Введите адрес доставки:</b>\n\n"
        "Улица, дом, квартира:",
        parse_mode="HTML"
    )
    await state.set_state(DeliveryState.entering_address)


@router.message(DeliveryState.entering_address)
async def enter_address(message: Message, state: FSMContext):
    """Ввод адреса"""
    await state.update_data(address=message.text)
    await message.answer(
        "📞 <b>Ваш контактный телефон?</b>\n\n"
        "Введите номер:",
        parse_mode="HTML"
    )
    await state.set_state(DeliveryState.entering_phone)


@router.message(DeliveryState.entering_phone)
async def enter_phone(message: Message, state: FSMContext):
    """Ввод телефона и показ подтверждения"""
    await state.update_data(phone=message.text)
    
    data = await state.get_data()
    filial_id = data.get("filial_id")
    filial_info = get_filial_info(filial_id)
    cart = data.get("cart", [])
    total = data.get("total_price", 0)
    
    confirmation_text = (
        "✅ <b>Подтверждение заказа доставки:</b>\n\n"
        f"📍 Ресторан: {filial_info.get('name')}\n"
        f"🏠 Адрес: {data.get('address')}\n"
        f"📞 Телефон: {data.get('phone')}\n\n"
        f"🛒 <b>Заказ:</b>\n"
    )
    
    for item in cart:
        item_total = item["price"] * item["quantity"]
        confirmation_text += f"• {item['name']} × {item['quantity']} = {item_total}₽\n"
    
    confirmation_text += f"\n💰 <b>Итого: {total}₽</b>\n\n"
    confirmation_text += "Подтвердить заказ?"
    
    await message.answer(
        confirmation_text, 
        parse_mode="HTML", 
        reply_markup=delivery_confirm_keyboard()
    )
    await state.set_state(DeliveryState.confirming)


@router.callback_query(DeliveryState.confirming, F.data == "delivery:confirm")
async def confirm_delivery(callback: CallbackQuery, state: FSMContext):
    """Подтверждение и сохранение заказа"""
    await callback.answer()
    
    data = await state.get_data()
    filial_id = data.get("filial_id")
    filial_info = get_filial_info(filial_id)
    cart = data.get("cart", [])
    total = data.get("total_price", 0)
    
    # Сохраняем в БД
    await save_order(
        user_id=callback.from_user.id,
        username=callback.from_user.username or callback.from_user.full_name,
        filial_id=filial_id,
        items=cart,
        total_price=total
    )
    
    # Экспортируем в Google Sheets
    try:
        export_order_to_sheet({
            "username": callback.from_user.username or callback.from_user.full_name,
            "filial_name": filial_info.get("name", ""),
            "items": ", ".join([f"{item['name']} × {item['quantity']}" for item in cart]),
            "total_price": total,
            "address": data.get("address"),
            "phone": data.get("phone")
        })
    except Exception as e:
        print(f"Ошибка экспорта в Google Sheets: {e}")
    
    await callback.message.edit_text(
        "✅ <b>Заказ принят!</b>\n\n"
        f"💰 Сумма: {total}₽\n"
        f"🏠 Адрес: {data.get('address')}\n\n"
        f"Мы свяжемся с вами по номеру {data.get('phone')} для подтверждения.",
        parse_mode="HTML"
    )
    await state.clear()


@router.callback_query(DeliveryState.confirming, F.data == "delivery:cancel")
async def cancel_delivery(callback: CallbackQuery, state: FSMContext):
    """Отмена заказа"""
    await callback.answer()
    
    data = await state.get_data()
    filial_id = data.get("filial_id")
    await state.clear()
    
    filial_info = get_filial_info(filial_id) if filial_id else {}
    
    await callback.message.edit_text(
        "❌ Заказ отменён",
        reply_markup=main_menu_keyboard(filial_info.get("has_delivery", False))
    )
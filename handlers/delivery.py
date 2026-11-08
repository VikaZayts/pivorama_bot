from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.filial import main_menu_keyboard
from keyboards.menu import menu_categories_keyboard, menu_items_keyboard
from keyboards.delivery import delivery_cart_keyboard
from data.filials import get_filial_info
from data.menu import MENU_CATEGORIES, get_item_by_id
from database import save_order
from utils.google_sheets import export_order_to_sheet

router = Router()

class DeliveryState(StatesGroup):
    viewing_menu = State()
    cart = State()
    entering_address = State()
    entering_phone = State()
    confirming = State()

@router.callback_query(F.data == "delivery")
async def start_delivery(callback: CallbackQuery, state: FSMContext):
    print("🚨 DEBUG 1: Нажата кнопка 'Заказать доставку'")
    await callback.answer()
    
    data = await state.get_data()
    filial_id = data.get("filial_id")
    filial_info = get_filial_info(filial_id)
    
    if not filial_info.get("has_delivery"):
        await callback.message.edit_text("❌ Доставка недоступна в этом филиале", reply_markup=main_menu_keyboard(False))
        return
    
    await callback.message.edit_text(
        "🚗 <b>Заказ доставки</b>\n\nВыберите категорию блюд:",
        parse_mode="HTML",
        reply_markup=menu_categories_keyboard()
    )
    await state.set_state(DeliveryState.viewing_menu)

@router.callback_query(DeliveryState.viewing_menu, F.data.startswith("menu_cat:"))
async def show_category_items(callback: CallbackQuery, state: FSMContext):
    print("🚨 DEBUG 2: Выбрана категория в доставке")
    await callback.answer()
    category_id = callback.data.split(":")[1]
    category = MENU_CATEGORIES.get(category_id, {})
    
    items_text = f"<b>{category['name']}</b>\n\n"
    for item in category.get("items", []):
        items_text += f"• {item['name']} ({item['weight']}) - <b>{item['price']}₽</b>\n"
    
    # Добавляем кнопку перехода в корзину прямо в меню категорий для удобства
    keyboard = menu_items_keyboard(category_id)
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🛒 Перейти к оформлению доставки", callback_data="delivery:show_cart")
    ])
    
    await callback.message.edit_text(items_text, parse_mode="HTML", reply_markup=keyboard)

@router.callback_query(DeliveryState.viewing_menu, F.data.startswith("add_item:"))
async def add_to_cart(callback: CallbackQuery, state: FSMContext):
    print("🚨 DEBUG 3: Блюдо добавлено в корзину доставки")
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
    await callback.answer(f"✅ {item['name']} добавлено в корзину доставки!")

@router.callback_query(F.data == "delivery:show_cart")
async def show_delivery_cart(callback: CallbackQuery, state: FSMContext):
    print("🚨 DEBUG 4: Открывается корзина доставки")
    await callback.answer()
    data = await state.get_data()
    cart = data.get("cart", [])
    
    if not cart:
        await callback.answer("🛒 Корзина пуста! Сначала добавьте блюда.")
        return
    
    cart_text = "🛒 <b>Ваш заказ на доставку:</b>\n\n"
    total = 0
    for item in cart:
        item_total = item["price"] * item["quantity"]
        total += item_total
        cart_text += f"• {item['name']} × {item['quantity']} = {item_total}₽\n"
    
    cart_text += f"\n💰 <b>Итого: {total}₽</b>"
    
    await state.update_data(total_price=total)
    await callback.message.edit_text(cart_text, parse_mode="HTML", reply_markup=delivery_cart_keyboard())
    await state.set_state(DeliveryState.cart)

@router.callback_query(DeliveryState.cart, F.data == "delivery:clear")
async def clear_delivery_cart(callback: CallbackQuery, state: FSMContext):
    print("🚨 DEBUG 5: Корзина доставки очищена")
    await callback.answer("🗑 Корзина очищена!")
    await state.update_data(cart=[])
    await callback.message.edit_text("🚗 <b>Заказ доставки</b>\n\nВыберите категорию блюд:", parse_mode="HTML", reply_markup=menu_categories_keyboard())
    await state.set_state(DeliveryState.viewing_menu)

@router.callback_query(DeliveryState.cart, F.data == "delivery:menu")
async def back_to_delivery_menu(callback: CallbackQuery, state: FSMContext):
    print("🚨 DEBUG 6: Возврат в меню доставки")
    await callback.answer()
    await callback.message.edit_text("🚗 <b>Заказ доставки</b>\n\nВыберите категорию блюд:", parse_mode="HTML", reply_markup=menu_categories_keyboard())
    await state.set_state(DeliveryState.viewing_menu)

@router.callback_query(DeliveryState.cart, F.data == "delivery:checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    print("🚨 DEBUG 7: Запрошен адрес доставки!")
    await callback.answer()
    await callback.message.edit_text(
        "🏠 <b>Введите адрес доставки:</b>\n\nУлица, дом, квартира:",
        parse_mode="HTML"
    )
    await state.set_state(DeliveryState.entering_address)

@router.message(DeliveryState.entering_address)
async def enter_address(message: Message, state: FSMContext):
    print(f"🚨 DEBUG 8: Получен адрес: {message.text}")
    await state.update_data(address=message.text)
    await message.answer("📞 <b>Ваш контактный телефон?</b>\n\nВведите номер:", parse_mode="HTML")
    await state.set_state(DeliveryState.entering_phone)

@router.message(DeliveryState.entering_phone)
async def enter_phone(message: Message, state: FSMContext):
    print(f"🚨 DEBUG 9: Получен телефон: {message.text}")
    await state.update_data(phone=message.text)
    
    data = await state.get_data()
    filial_id = data.get("filial_id")
    filial_info = get_filial_info(filial_id)
    cart = data.get("cart", [])
    total = data.get("total_price", 0)
    
    confirmation_text = f"✅ <b>Подтверждение заказа доставки:</b>\n\n📍 Ресторан: {filial_info.get('name')}\n🏠 Адрес: {data.get('address')}\n📞 Телефон: {data.get('phone')}\n\n🛒 <b>Заказ:</b>\n"
    for item in cart:
        confirmation_text += f"• {item['name']} × {item['quantity']} = {item['price'] * item['quantity']}₽\n"
    confirmation_text += f"\n💰 <b>Итого: {total}₽</b>\n\nПодтвердить заказ?"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="delivery:confirm")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="delivery:cancel")]
    ])
    
    await message.answer(confirmation_text, parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(DeliveryState.confirming)

@router.callback_query(DeliveryState.confirming, F.data == "delivery:confirm")
async def confirm_delivery(callback: CallbackQuery, state: FSMContext):
    print("🚨 DEBUG 10: Заказ доставки подтвержден и сохранен!")
    await callback.answer()
    data = await state.get_data()
    filial_id = data.get("filial_id")
    filial_info = get_filial_info(filial_id)
    cart = data.get("cart", [])
    total = data.get("total_price", 0)
    
    await save_order(user_id=callback.from_user.id, username=callback.from_user.username or callback.from_user.full_name, filial_id=filial_id, items=cart, total_price=total)
    
    try:
        export_order_to_sheet({"username": callback.from_user.username or callback.from_user.full_name, "filial_name": filial_info.get("name", ""), "items": ", ".join([f"{item['name']} × {item['quantity']}" for item in cart]), "total_price": total, "address": data.get("address"), "phone": data.get("phone")})
    except Exception as e:
        print(f"Ошибка Google Sheets (это нормально, если не настроено): {e}")
    
    await callback.message.edit_text(f"✅ <b>Заказ принят!</b>\n\n💰 Сумма: {total}₽\n🏠 Адрес: {data.get('address')}\n\nМы свяжемся с вами по номеру {data.get('phone')}.", parse_mode="HTML")
    await state.clear()

@router.callback_query(DeliveryState.confirming, F.data == "delivery:cancel")
async def cancel_delivery(callback: CallbackQuery, state: FSMContext):
    print("🚨 DEBUG 11: Заказ доставки отменен")
    await callback.answer()
    data = await state.get_data()
    filial_id = data.get("filial_id")
    await state.clear()
    filial_info = get_filial_info(filial_id) if filial_id else {}
    await callback.message.edit_text("❌ Заказ отменён", reply_markup=main_menu_keyboard(filial_info.get("has_delivery", False)))
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.menu import menu_categories_keyboard, menu_items_keyboard, cart_keyboard
from keyboards.filial import main_menu_keyboard
from data.menu import MENU_CATEGORIES, get_item_by_id
from data.filials import get_filial_info
from database import save_order
from utils.google_sheets import export_order_to_sheet

router = Router()


class OrderState(StatesGroup):
    """Состояния для оформления заказа"""
    viewing_menu = State()
    cart = State()
    confirming = State()


@router.callback_query(F.data == "menu")
async def show_menu(callback: CallbackQuery, state: FSMContext):
    """Показать категории меню"""
    await callback.answer()
    await callback.message.edit_text(
        "🍽 <b>Выберите категорию:</b>",
        parse_mode="HTML",
        reply_markup=menu_categories_keyboard()
    )
    await state.set_state(OrderState.viewing_menu)


@router.callback_query(OrderState.viewing_menu, F.data.startswith("menu_cat:"))
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


@router.callback_query(OrderState.viewing_menu, F.data.startswith("add_item:"))
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


@router.callback_query(OrderState.viewing_menu, F.data == "checkout")
async def show_cart(callback: CallbackQuery, state: FSMContext):
    """Показать корзину"""
    await callback.answer()
    data = await state.get_data()
    cart = data.get("cart", [])
    filial_id = data.get("filial_id")

    if not cart:
        await callback.answer("🛒 Корзина пуста!")
        return

    cart_text = "🛒 <b>Ваш заказ:</b>\n\n"
    total = 0

    for item in cart:
        item_total = item["price"] * item["quantity"]
        total += item_total
        cart_text += f"• {item['name']} × {item['quantity']} = {item_total}₽\n"

    cart_text += f"\n💰 <b>Итого: {total}₽</b>\n\n"
    cart_text += "Оформить заказ?"

    await state.update_data(total_price=total)
    await callback.message.edit_text(
        cart_text,
        parse_mode="HTML",
        reply_markup=cart_keyboard()
    )
    await state.set_state(OrderState.confirming)


@router.callback_query(OrderState.confirming, F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery, state: FSMContext):
    """Очистить корзину"""
    await callback.answer("🗑 Корзина очищена!")
    await state.update_data(cart=[])
    await callback.message.edit_text(
        "🍽 <b>Выберите категорию:</b>",
        parse_mode="HTML",
        reply_markup=menu_categories_keyboard()
    )
    await state.set_state(OrderState.viewing_menu)


@router.callback_query(OrderState.confirming, F.data == "checkout")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    """Подтвердить и сохранить заказ"""
    await callback.answer()

    data = await state.get_data()
    cart = data.get("cart", [])
    total = data.get("total_price", 0)
    filial_id = data.get("filial_id")

    if not cart:
        await callback.answer("🛒 Корзина пуста!")
        return

    # Сохраняем заказ в БД
    await save_order(
        user_id=callback.from_user.id,
        username=callback.from_user.username or callback.from_user.full_name,
        filial_id=filial_id,
        items=cart,
        total_price=total
    )

    # Экспортируем в Google Sheets (с обработкой ошибок)
    try:
        filial_info = get_filial_info(filial_id) if filial_id else {}
        export_order_to_sheet({
            "username": callback.from_user.username or callback.from_user.full_name,
            "filial_name": filial_info.get("name", ""),
            "items": ", ".join([f"{item['name']} × {item['quantity']}" for item in cart]),
            "total_price": total
        })
    except Exception as e:
        print(f"Ошибка экспорта в Google Sheets: {e}")

    filial_info = get_filial_info(filial_id) if filial_id else {}

    await callback.message.edit_text(
        f"✅ <b>Заказ принят!</b>\n\n"
        f"💰 Сумма: {total}₽\n"
        f"📍 Ресторан: {filial_info.get('name', '')}\n\n"
        f"Мы свяжемся с вами для подтверждения.",
        parse_mode="HTML"
    )

    # Очищаем корзину
    await state.clear()


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await callback.answer()
    data = await state.get_data()
    filial_id = data.get("filial_id")
    filial_info = get_filial_info(filial_id) if filial_id else {}

    # Очищаем состояние заказа, но сохраняем filial_id
    cart = data.get("cart", [])
    await state.clear()
    if filial_id:
        await state.update_data(filial_id=filial_id)

    await callback.message.edit_text(
        f"🍺 <b>{filial_info.get('name', 'Ресторан')}</b>\n\n"
        f"📍 {filial_info.get('address', '')}\n"
        f"📞 {filial_info.get('phone', '')}\n\n"
        f"Выберите действие:",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(filial_info.get("has_delivery", False))
    )
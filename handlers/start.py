from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards.filial import filial_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "🍺 <b>Добро пожаловать в Пивораму!</b>\n\n"
        "Выберите ресторан:",
        parse_mode="HTML",
        reply_markup=filial_keyboard()
    )
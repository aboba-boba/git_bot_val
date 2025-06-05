from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

clear_favorites_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("Очистить список", callback_data="clear_favorites")
)
from aiogram.dispatcher.filters import BoundFilter
from admin_setup.admin_settings import is_admin
class AdminFilter(BoundFilter):
    async def check(self, message):
        return is_admin(message.from_user.id)


# BAN filter

from aiogram.dispatcher.middlewares import BaseMiddleware

class BanMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message, data):
        try:
            with open("banned.txt", "r") as f:
                banned = [line.strip() for line in f]
            if str(message.from_user.id) in banned:
                await message.answer("Бан + расстрел.")
                raise Exception("Banned")
        except FileNotFoundError:
            pass
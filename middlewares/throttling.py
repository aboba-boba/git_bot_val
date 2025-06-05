# anti spam
import time
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit=1.0):
        super().__init__()
        self.rate_limit = rate_limit
        self.last_time = {}

    async def on_pre_process_message(self, message: types.Message, data: dict):
        user_id = message.from_user.id
        now = time.time()
        last = self.last_time.get(user_id, 0)
        if now - last < self.rate_limit:
            await message.answer("Не кипишуй!\n"
                                 "やめてください!"
                                 )
            raise Exception("Throttled")
        self.last_time[user_id] = now
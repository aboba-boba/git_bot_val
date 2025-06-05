from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config.settings import TG_TOKEN, logger
from services.agent_api import fetch_agents, get_agent_info
from services.favorites import get_favorites, add_favorite, remove_favorite
from keyboards.my_agent_button import kb
from keyboards.inline_button import clear_favorites_kb
from middlewares.throttling import ThrottlingMiddleware
from filters.admin_filter import AdminFilter, BanMiddleware
from admin_setup.admin_settings import is_admin


bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(ThrottlingMiddleware(rate_limit=1.0))
dp.filters_factory.bind(AdminFilter)
dp.middleware.setup(BanMiddleware())

#Start message
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    logger.info("Получен /start от %s", message.from_user.id)
    await message.answer(
        "Привет! Я — Valorant Agent Guru.\n",
        reply_markup=kb
    )

#Help list, agents n other commands
@dp.message_handler(commands=["help"])
async def cmd_help(message: types.Message):
    logger.info("Получен /help от %s", message.from_user.id)
    await message.answer(
        "Список команд:\n"
        "/start — запустить бота\n"
        "/help — показать этот список\n"
        "/agentinfo [имя] — инфо агента\n"
        "/favorite add|remove [имя] — добавить/убрать из избранного\n"
        "/listfavorites — мои избранные агенты\n"
        "/listagents — список всех агентов\n"
    )

@dp.message_handler(commands=["listagents"])
async def cmd_listagents(message: types.Message):
    agents = await fetch_agents()
    names = [
        a["displayName"]
        for a in agents
        if a.get("isPlayableCharacter", False)
    ]
    await message.answer("Список агентов:\n" + "\n".join(names))

@dp.message_handler(commands=["agentinfo"])
async def cmd_agentinfo(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer("Укажи имя: /agentinfo Jett")
    name = parts[1]
    try:
        info = await get_agent_info(name)
        await message.answer(info, parse_mode=types.ParseMode.MARKDOWN)
    except Exception as e:
        logger.exception("Ошибка в get_agent_info")
        await message.answer(f"⚠️ Произошла ошибка: {e}")

@dp.message_handler(commands=["favorite"])
async def cmd_favorite(message: types.Message):
    args = message.get_args().split()
    if len(args) < 2:
        await message.answer("Используйте: /favorite add|remove [имя агента]")
        return

    action, name = args[0].lower(), " ".join(args[1:])

    # Получаем список всех агентов
    agents = await fetch_agents()
    # Словарь: имя в нижнем регистре -> оригинальное имя
    agent_map = {agent["displayName"].lower(): agent["displayName"] for agent in agents}

    agent_name_correct = agent_map.get(name.lower())
    if not agent_name_correct:
        await message.answer("Такого агента не существует!")
        return

    if action == "add":
        if add_favorite(message.from_user.id, agent_name_correct):
            await message.answer(f"✅ {agent_name_correct} добавлен в избранное.")
        else:
            await message.answer(f"{agent_name_correct} уже в избранном.")
    elif action == "remove":
        if remove_favorite(message.from_user.id, agent_name_correct):
            await message.answer(f"✅ {agent_name_correct} удалён из избранного.")
        else:
            await message.answer(f"{agent_name_correct} не найден в избранном.")
    else:
        await message.answer("Используйте: /favorite add|remove [имя агента]")

@dp.message_handler(commands=["listfavorites"])
async def cmd_listfavorites(message: types.Message):
    user_id = message.from_user.id
    favorites = get_favorites(user_id)
    if favorites:
        await message.answer(
            "Ваши любимые агенты:\n" + "\n".join(favorites),
            reply_markup=clear_favorites_kb
        )
    else:
        await message.answer("У вас пока нет любимых агентов.")
        
# inline clean        
@dp.callback_query_handler(lambda c: c.data == "clear_favorites")
async def clear_favorites_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    from services.favorites import _load, _save
    data = _load()
    user_key = str(user_id)
    if user_key in data:
        data[user_key] = [] 
        _save(data)
        await callback_query.message.edit_text("Список любимых агентов очищен!")
    else:
        await callback_query.answer("Список уже пуст.", show_alert=True)
# adding inline button
@dp.message_handler(lambda message: message.text == "Мои агенты")
async def handle_my_agents(message: types.Message):
    user_id = message.from_user.id
    favorites = get_favorites(user_id)
    if favorites:
        await message.answer(
            "Ваши любимые агенты:\n" + "\n".join(favorites),
            reply_markup=clear_favorites_kb 
        )
    else:
        await message.answer("У вас пока нет любимых агентов. Добавьте их через /favorite add [имя]")

# help button
@dp.message_handler(lambda message: message.text == "Помощь")
async def handle_help_button(message: types.Message):
    await message.answer(
        "Список команд:\n"
        "/start — запустить бота\n"
        "/help — показать этот список\n"
        "/agentinfo [имя] — инфо агента\n"
        "/favorite add|remove [имя] — добавить/убрать из избранного\n"
        "/listfavorites — мои избранные агенты\n"
        "/listagents — список всех агентов\n"
    )
    


# admin commands

# users counter
@dp.message_handler(commands=["stats"])
async def cmd_stats(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    from services.favorites import _load
    data = _load()
    await message.answer(f"Рабов: {len(data)}")

# all scream
@dp.message_handler(commands=["broadcast"])
async def cmd_broadcast(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Введите текст рассылки:")

    @dp.message_handler(lambda m: m.from_user.id == message.from_user.id)
    async def process_broadcast(msg: types.Message):
        text = msg.text
        from services.favorites import _load
        data = _load()
        count = 0
        for uid in data.keys():
            try:
                await bot.send_message(uid, f"КОРОЛЬ ГОВОРИТ:\n{text}")
                count += 1
            except:
                pass
        await msg.answer(f"Рассылка завершена. Отправлено {count} рабам.")
        dp.message_handlers.unregister(process_broadcast)

# insult to the administration
@dp.message_handler(commands=["ban"])
async def cmd_ban(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    args = message.get_args().split()
    if not args:
        await message.answer("Укажите user_id для бана.")
        return
    ban_id = args[0]
    with open("banned.txt", "a") as f:
        f.write(ban_id + "\n")
    await message.answer(f"Пользователь {ban_id} заблокирован.")

# payment for admins
@dp.message_handler(commands=["unban"])
async def cmd_unban(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    args = message.get_args().split()
    if not args:
        await message.answer("Укажите user_id для разбана.")
        return
    unban_id = args[0]
    try:
        with open("banned.txt", "r") as f:
            banned = [line.strip() for line in f if line.strip()]
        if unban_id in banned:
            banned.remove(unban_id)
            with open("banned.txt", "w") as f:
                for uid in banned:
                    f.write(uid + "\n")
            await message.answer(f"Пользователь {unban_id} разбанен.")
        else:
            await message.answer("Пользователь не найден в списке забаненных.")
    except FileNotFoundError:
        await message.answer("Список забаненных пуст.")

if __name__ == "__main__":
    logger.info("Бот запускается…")
    executor.start_polling(dp, skip_updates=True)

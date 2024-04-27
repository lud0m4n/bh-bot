from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiohttp import web
import os
from dotenv import load_dotenv
import asyncio
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv('API_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def butt(txt):
    kb = [[types.KeyboardButton(text=txt)]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите...")
    return keyboard

user_dict = {}  # Пустой словарь для хранения соответствия username к chat_id

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    chat_id = message.chat.id
    username = message.from_user.username  # Получаем username пользователя
    if username:
        user_dict[username] = chat_id  # Сохраняем chat_id по username
    await message.answer("Добро пожаловать!")

async def send_notification(username):
    print(user_dict)
    chat_id = user_dict.get(username)
    if chat_id:
        try:
            await bot.send_message(chat_id, f"{username}, Вы были выбраны, как исполнитель срочного таска!")
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {username}: {e}")
    else:
        print(f"Chat ID для пользователя {username} не найден.")


async def handle(request):
    try:
        data = await request.json()
        username = data.get('username')  # Получаем username из запроса
        if not username:
            raise ValueError("Username is required")
        await send_notification(username)
        return web.Response(text="Уведомление отправлено")
    except ValueError as e:
        return web.Response(text=str(e), status=400)
    except Exception as e:
        return web.Response(text=f"Не удалось обработать запрос: {e}", status=500)

app = web.Application()
app.add_routes([web.post('/notify', handle)])

async def main():
    # Запуск сервера и поллинга бота
    bot_task = dp.start_polling(bot)
    web_task = web._run_app(app, port=8080)
    await asyncio.gather(bot_task, web_task)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

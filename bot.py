import asyncio
import os
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

bot = Bot(os.environ["BOT_TOKEN"])
CHAT_ID = int(os.environ["ADMIN_CHAT_ID"])
dp = Dispatcher()

db = sqlite3.connect("feedback.db")
db.execute(
    "CREATE TABLE IF NOT EXISTS map ("
    "msg_id INTEGER PRIMARY KEY, user_id INTEGER, user_msg_id INTEGER)"
)


WELCOME = "Перешлите скриншот оплаты, ваше имя и первую букву фамилии"


@dp.message(CommandStart(), F.chat.type == "private")
async def start(m: Message):
    await m.answer(WELCOME)


@dp.message(F.chat.type == "private")
async def from_user(m: Message):
    fwd = await m.forward(CHAT_ID)
    db.execute(
        "INSERT OR REPLACE INTO map VALUES (?,?,?)",
        (fwd.message_id, m.chat.id, m.message_id),
    )
    db.commit()


@dp.message(F.chat.id == CHAT_ID, F.reply_to_message)
async def from_admin(m: Message):
    row = db.execute(
        "SELECT user_id, user_msg_id FROM map WHERE msg_id=?",
        (m.reply_to_message.message_id,),
    ).fetchone()
    if row:
        await bot.copy_message(
            row[0], m.chat.id, m.message_id, reply_to_message_id=row[1]
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

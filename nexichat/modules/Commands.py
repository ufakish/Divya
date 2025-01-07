import random
import os
import shutil
from MukeshAPI import api
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.errors import MessageEmpty
from pyrogram.enums import ChatAction, ChatMemberStatus as CMS
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from deep_translator import GoogleTranslator
from nexichat.database.chats import add_served_chat
from nexichat.database.users import add_served_user
from config import MONGO_URL, OWNER_ID
from nexichat import nexichat, mongo, LOGGER, db
from nexichat.modules.helpers import chatai, storeai, languages, CHATBOT_ON
from nexichat.modules.helpers import (
    ABOUT_BTN,
    ABOUT_READ,
    ADMIN_READ,
    BACK,
    CHATBOT_BACK,
    CHATBOT_READ,
    DEV_OP,
    HELP_BTN,
    HELP_READ,
    MUSIC_BACK_BTN,
    SOURCE_READ,
    START,
    TOOLS_DATA_READ,
)
import asyncio

translator = GoogleTranslator()

lang_db = db.ChatLangDb.LangCollection
status_db = db.chatbot_status_db.status


@nexichat.on_message(
    filters.command(["restart"]) & filters.user(int(OWNER_ID))
)
async def restart(client: Client, message: Message):
    reply = await message.reply_text("**🔁 Rᴇsᴛᴀʀᴛɪɴɢ 🔥 ...**")
    await message.delete()
    await reply.edit_text("🥀 SᴜᴄᴄᴇssFᴜʟʟʏ RᴇSᴛᴀʀᴛᴇᴅ\n ︎ᴄʜᴀᴛʙᴏᴛ  🔥 ...\n\n💕 Pʟᴇᴀsᴇ Wᴀɪᴛ 5 ꜱᴇᴄ Fᴏʀ\nLᴏᴀᴅ Usᴇʀ Pʟᴜɢɪɴs ✨ ...</b>")
    os.system(f"kill -9 {os.getpid()} && bash start")
    
def generate_language_buttons(languages):
    buttons = []
    current_row = []
    for lang, code in languages.items():
        current_row.append(InlineKeyboardButton(lang.capitalize(), callback_data=f'setlang_{code}'))
        if len(current_row) == 4:
            buttons.append(current_row)
            current_row = []
    if current_row:
        buttons.append(current_row)
    return InlineKeyboardMarkup(buttons)

async def get_chat_language(chat_id):
    chat_lang = await lang_db.find_one({"chat_id": chat_id})
    return chat_lang["language"] if chat_lang and "language" in chat_lang else "en"
    
@nexichat.on_message(filters.command(["lang", "language", "setlang"]))
async def set_language(client: Client, message: Message):
    await message.reply_text(
        "Please select your chat language:",
        reply_markup=generate_language_buttons(languages)
    )


@nexichat.on_message(filters.command("status"))
async def status_command(client: Client, message: Message):
    chat_id = message.chat.id
    chat_status = await status_db.find_one({"chat_id": chat_id})
    if chat_status:
        current_status = chat_status.get("status", "not found")
        await message.reply(f"Chatbot status for this chat: **{current_status}**")
    else:
        await message.reply("No status found for this chat.")


@nexichat.on_message(filters.command(["lang", "language", "setlang"]))
async def set_language(client: Client, message: Message):
    await message.reply_text(
        "Please select your chat language:",
        reply_markup=generate_language_buttons(languages)
    )


@nexichat.on_message(filters.command(["resetlang", "nolang"]))
async def reset_language(client: Client, message: Message):
    chat_id = message.chat.id
    lang_db.update_one({"chat_id": chat_id}, {"$set": {"language": "nolang"}}, upsert=True)
    await message.reply_text("**Bot language has been reset in this chat to mix language.**")


@nexichat.on_message(filters.command("chatting"))
async def chatbot_command(client: Client, message: Message):
    await message.reply_text(
        f"Chat: {message.chat.title}\n**Choose an option to YES/NO the chatbot.**",
        reply_markup=InlineKeyboardMarkup(CHATBOT_ON),
    )

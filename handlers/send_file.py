# (c) @FarshidBand

import asyncio
from configs import Config
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from handlers.helpers import str_to_b64


async def ReplyForward(message: Message, file_id: int):
    try:
        await message.reply_text(
            f"**🔺لینک  اشتراک گذاری این فایل 👇**\n"
            f"https://t.me/{Config.BOT_USERNAME}?start=SeriesPlus1_{str_to_b64(str(file_id))}\n\n"
            f"__• برای دریافت فایل روی لینک کلیک کنید👆__\n‌**⚠️⁩ این لینک تا 7 روز معتبر می باشد.**",
            disable_web_page_preview=True, quote=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await ReplyForward(message, file_id)


async def MediaForward(bot: Client, user_id: int, file_id: int):
    try:
        if Config.FORWARD_AS_COPY is True:
            return await bot.copy_message(chat_id=user_id, from_chat_id=Config.DB_CHANNEL,
                                          message_id=file_id)
        elif Config.FORWARD_AS_COPY is False:
            return await bot.forward_messages(chat_id=user_id, from_chat_id=Config.DB_CHANNEL,
                                              message_ids=file_id)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return MediaForward(bot, user_id, file_id)


async def SendMediaAndReply(bot: Client, user_id: int, file_id: int):
    sent_message = await MediaForward(bot, user_id, file_id)
    await ReplyForward(message=sent_message, file_id=file_id)
    await asyncio.sleep(2)

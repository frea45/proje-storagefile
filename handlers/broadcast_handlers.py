# (c) @farshidband

import time
import string
import random
import datetime
import aiofiles
import asyncio
import traceback
import aiofiles.os
from configs import Config
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid

broadcast_ids = {}


async def send_msg(user_id, message):
    try:
        if Config.BROADCAST_AS_COPY is False:
            await message.forward(chat_id=user_id)
        elif Config.BROADCAST_AS_COPY is True:
            await message.copy(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"


async def main_broadcast_handler(m, db):
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for i in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break
    out = await m.reply_text(
        text=f"**•پخش ارسال این پیام به کاربران شروع شد.**\n\n**📌هنگامی که همه کابران مطلع شدند در قالب فایلی اطلاع رسانی میشود.**"
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(
        total=total_users,
        current=done,
        failed=failed,
        success=success
    )
    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for user in all_users:
            sts, msg = await send_msg(
                user_id=int(user['id']),
                message=broadcast_msg
            )
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await db.delete_user(user['id'])
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(
                    dict(
                        current=done,
                        failed=failed,
                        success=success
                    )
                )
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await asyncio.sleep(3)
    await out.delete()
    if failed == 0:
        await m.reply_text(
            text=f"**♨️ارسال پیام همگانی در تایم{completed_in} انجام شد**`\n\n**👥 تعداد کاربران :** {total_users} نفر\n**✉️ مجموع انجام شده پیام :** {done}\n**✅ تعداد ارسال موفق :** {success}\n**❌ تعداد ارسال ناموفق :** {failed}",
            quote=True
        )
    else:
        await m.reply_document(
            document='broadcast.txt',
            caption=f"**♨️ارسال پیام همگانی در تایم`{completed_in} انجام شد**`\n\n**👥 تعداد کاربران :** {total_users} نفر\n**✉️ مجموع انجام شده پیام :** {done}\n**✅ تعداد ارسال موفق :** {success}\n**❌ تعداد ارسال ناموفق :** {failed}",
            quote=True
        )
    await aiofiles.os.remove('broadcast.txt')

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from Config import MUST_JOIN


@Client.on_message(~filters.edited & filters.incoming & filters.private, group=-1)
async def must_join_channel(bot: Client, msg: Message):
    if not MUST_JOIN:  # Not compulsory
        return
    try:
        try:
            await bot.get_chat_member(MUST_JOIN, msg.from_user.id)
        except UserNotParticipant:
            if MUST_JOIN.isalpha():
                link = "https://t.me/" + MUST_JOIN
            else:
                chat_info = await bot.get_chat(MUST_JOIN)
                link = chat_info.invite_link
            try:
                await msg.reply(
                    f"🚨يجب ان تشترك في قناة [🔮𝐒𝐎𝐔𝐑𝐂𝐄 𝐕𝘼𝙈𝘽𝙄𝙍🔮]({https://t.me/XxvprxX}) حتى تتمكن من استخدام الخدمه بعد الاشتراك قم بضغط علي استارت مره اخري.",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✅اضـغط للأشتـراك بالـقـنـاه✅", url=link)]
                    ])
                )
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        print(f"انا لست ادمن في القناه MUST_JOIN  : {MUST_JOIN} !")

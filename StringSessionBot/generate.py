from asyncio.exceptions import TimeoutError
from Data import Data
from pyrogram import Client, filters
from telethon import TelegramClient
from telethon.sessions import StringSession
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)


@Client.on_message(filters.private & ~filters.forwarded & filters.command('generate'))
async def main(_, msg):
    await msg.reply(
        "📟اذا كنـت تـريد تنـصيـب سـورس مـيوزك فـأختـار كــود بـايـروجـرام, واذا تـريـد تنـصـيب التليثون فـأخـتار كــود تيرمكـس",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🎧¦كــود بـايـروجـرام", callback_data="pyrogram"),
            InlineKeyboardButton("🌐¦كــود تيرمكـس", callback_data="telethon")
        ]])
    )


async def generate_session(bot, msg, telethon=False):
    await msg.reply("🌐بدا عمل جلسه {} واستخراج الكود...".format("تليـثون" if telethon else "مـيـوزك"))
    user_id = msg.chat.id
    api_id_msg = await bot.ask(user_id, '🎮أولا قم بأرسال الـ `API_ID`', filters=filters.text)
    if await cancelled(api_id_msg):
        return
    try:
        api_id = int(api_id_msg.text)
    except ValueError:
        await api_id_msg.reply('❌يوجد خطأ في الـ API_ID . ☑️من فضلك ابدأ عمل جلسه مره اخري.', quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    api_hash_msg = await bot.ask(user_id, '🎮حسنـا قم بأرسال الـ `API_HASH`', filters=filters.text)
    if await cancelled(api_id_msg):
        return
    api_hash = api_hash_msg.text
    phone_number_msg = await bot.ask(user_id, '✔️الان ارسل `رقمك` مع رمز دولتك , مثال :`+201288458064`', filters=filters.text)
    if await cancelled(api_id_msg):
        return
    phone_number = phone_number_msg.text
    await msg.reply("⬇️انتـظر لـحظـه سـوف نـرسـل كـود لحسابـك بالتليجـرام...")
    if telethon:
        client = TelegramClient(StringSession(), api_id, api_hash)
    else:
        client = Client(":memory:", api_id, api_hash)
    await client.connect()
    try:
        if telethon:
            code = await client.send_code_request(phone_number)
        else:
            code = await client.send_code(phone_number)
    except (ApiIdInvalid, ApiIdInvalidError):
        await msg.reply('`API_ID` و `API_HASH` ❌هذه الايبيهات خطأ. ☑️من فضلك ابدأ عمل جلسه مره اخري', reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        await msg.reply('`رقمك` ❌خطأ. رجاءا قم بأعادة الاستخراج من جديد.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    try:
        phone_code_msg = await bot.ask(user_id, " 🔍من فضلك افحص حسابك بالتليجرام وتفقد الكود من حساب اشعارات التليجرام. إذا كان هناك تحقق بخطوتين( المرور ) ، أرسل كلمة المرور هنا بعد ارسال كود الدخول بالتنسيق أدناه.- اذا كانت كلمة المرور او الكود  هي 12345 يرجى ارسالها بالشكل التالي 1 2 3 4 5 مع وجود مسـافـات بين الارقام اذا احتجت مساعدة @XxlllllllllllllllllllllllllllxX", filters=filters.text, timeout=600)
        if await cancelled(api_id_msg):
            return
    except TimeoutError:
        await msg.reply('❌عذرا لقد تخطيت 10 دقائق من الزمن المحدد. ☑️من فضلك ابدأ عمل جلسه مره اخري.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    phone_code = phone_code_msg.text.replace(" ", "")
    try:
        if telethon:
            await client.sign_in(phone_number, phone_code, password=None)
        else:
            await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except (PhoneCodeInvalid, PhoneCodeInvalidError):
        await msg.reply('❌الكود غير صحيح. ☑️من فضلك ابدأ عمل جلسه مره اخري.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    except (PhoneCodeExpired, PhoneCodeExpiredError):
        await msg.reply('❌الكود هذا انتهت صلاحيته. ☑️من فضلك ابدأ عمل جلسه مره اخري.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    except (SessionPasswordNeeded, SessionPasswordNeededError):
        try:
            two_step_msg = await bot.ask(user_id, 'هذا الحساب محمي من خلال التحقق بخطوتين. من فضلك ارسل 🔑 كلمه االمرور .', filters=filters.text, timeout=300)
        except TimeoutError:
            await msg.reply('❌عذرا لقد تخطيت 5 دقائق من الزمن المحدد. ☑️من فضلك ابدأ عمل جلسه مره اخري.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
            return
        try:
            password = two_step_msg.text
            if telethon:
                await client.sign_in(password=password)
            else:
                await client.check_password(password=password)
            if await cancelled(api_id_msg):
                return
        except (PasswordHashInvalid, PasswordHashInvalidError):
            await two_step_msg.reply('❌كلمه المرور خطأ. ☑️من فضلك ابدأ عمل جلسه مره اخري.', quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
            return
    if telethon:
        string_session = client.session.save()
    else:
        string_session = await client.export_session_string()
    text = "**{} جـلسـه جـديـده** \n\n`{}` \n\nاستخرجت من @VPlllllllbot".format("⬇️تـلـيـثـــون" if telethon else "⬇️مـــيـــوزك", string_session)
    try:
        await client.send_message("me", text)
    except KeyError:
        pass
    await client.disconnect()
    await phone_code_msg.reply("✅تم استخراج الجلسه بنجاح {}. \n\n🔍من فضلك تفحص الرسايل المحفوظه بحسابك! \n\nBy @VPlllllllbot".format("telethon" if telethon else "pyrogram"))


async def cancelled(msg):
    if "/cancel" in msg.text:
        await msg.reply("✔️تم الغاء الاستخراج!", quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return True
    elif "/restart" in msg.text:
        await msg.reply("🌀تمت اعاده تشغيل البوت !", quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return True
    elif msg.text.startswith("/"):  # Bot Commands
        await msg.reply("♨️تم ألغاء الاستخراج!", quote=True)
        return True
    else:
        return False

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import asyncio
import random
import os
import json

API_ID = 25266397
API_HASH = "f2a1ca192e6515e9df958c8011741207"
BOT_TOKEN = "7883811901:AAGlWec5lNXp6drl1StLnXIR6PQvTPGfdzM"

CHANNEL_1 = "ANumMo"
CHANNEL_2 = "TNumMo"

app = Client("NumMo_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

VERIFIED_FILE = "verified_users.txt"
ACCOUNTS_FILE = "accounts.json"

if os.path.exists(VERIFIED_FILE):
    with open(VERIFIED_FILE, "r") as f:
        verified_users = set(int(line.strip()) for line in f if line.strip())
else:
    verified_users = set()

if os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, "r") as f:
        user_accounts = json.load(f)
else:
    user_accounts = {}

def save_accounts():
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(user_accounts, f)

def save_verified_user(user_id):
    with open(VERIFIED_FILE, "a") as f:
        f.write(f"{user_id}\n")

def generate_unique_email():
    while True:
        random_part = ''.join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8))
        email = f"{random_part}@NUMMO.com"
        if email not in user_accounts.values():
            return email

async def check_subscriptions(client, user_id):
    results = {}
    try:
        ch1 = await client.get_chat_member(CHANNEL_1, user_id)
        results["ch1"] = ch1.status not in ["left", "kicked"]
    except:
        results["ch1"] = False
    try:
        ch2 = await client.get_chat_member(CHANNEL_2, user_id)
        results["ch2"] = ch2.status not in ["left", "kicked"]
    except:
        results["ch2"] = False
    return results

pending_challenges = {}

async def send_verification_question(client, message):
    user_id = message.from_user.id
    num1 = random.randint(1, 7)
    num2 = random.randint(1, 7)
    answer = num1 * num2
    pending_challenges[user_id] = answer
    await message.reply_text(
        f"🤖 للتأكد من أنك إنسان، أجب على هذا السؤال:\n\n"
        f"❓ كم حاصل: {num1} × {num2} ؟\n\n"
        f"✏️ أرسل الإجابة كرقم فقط."
    )

async def send_welcome_message(client, target):
    user = target.from_user
    full_name = (user.first_name or '') + ' ' + (user.last_name or '')
    welcome_text = (
        f"✨ أهلاً وسهلاً بك ({full_name.strip()}) في بوت *NuMMo🇾🇪* الأفضل لخدمات الأرقام الوهمية!\n\n"
        "✅ يمكنك الآن الاستفادة من أكثر من 180 دولة وخدمة، تشمل:\n"
        "📱 واتساب، تيليجرام، فيسبوك، تويتر، وغيرها الكثير!\n\n"
        "⚡ استمتع بأفضل العروض، وواجهة سهلة وسريعة، وخدمة عملاء مميزة."
    )
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✳️ إنشاء حساب جديد", callback_data="create_account"),
         InlineKeyboardButton("✨ تسجيل الدخول", callback_data="login_account")],
        [InlineKeyboardButton("ℹ️ تعليمات البوت", callback_data="bot_help")],
        [InlineKeyboardButton("⚖️ شروط الاستخدام", callback_data="terms_of_use")]
    ])
    if isinstance(target, Message):
        await target.reply_text(welcome_text, reply_markup=markup)
    else:
        await target.message.edit_text(welcome_text, reply_markup=markup)

@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    subs = await check_subscriptions(client, user_id)
    if subs["ch1"] and subs["ch2"]:
        if user_id in verified_users:
            await send_welcome_message(client, message)
        else:
            await send_verification_question(client, message)
    else:
        btns = []
        if not subs["ch1"]:
            btns.append([InlineKeyboardButton("📢 القناة الرسمية", url=f"https://t.me/{CHANNEL_1}")])
        if not subs["ch2"]:
            btns.append([InlineKeyboardButton("✅ قناة التفعيلات", url=f"https://t.me/{CHANNEL_2}")])
        btns.append([InlineKeyboardButton("🔁 تحقق من الاشتراك", callback_data="check_sub")])
        await message.reply_text(
            "⚠️ يجب الاشتراك في القنوات التالية لتتمكن من استخدام البوت:",
            reply_markup=InlineKeyboardMarkup(btns)
        )

@app.on_callback_query(filters.regex("check_sub"))
async def check_subscription(client, callback_query):
    user_id = callback_query.from_user.id
    subs = await check_subscriptions(client, user_id)
    if subs["ch1"] and subs["ch2"]:
        await callback_query.message.delete()
        if user_id in verified_users:
            await send_welcome_message(client, callback_query)
        else:
            await send_verification_question(client, callback_query.message)
    else:
        btns = []
        if not subs["ch1"]:
            btns.append([InlineKeyboardButton("📢 القناة الرسمية", url=f"https://t.me/{CHANNEL_1}")])
        if not subs["ch2"]:
            btns.append([InlineKeyboardButton("✅ قناة التفعيلات", url=f"https://t.me/{CHANNEL_2}")])
        btns.append([InlineKeyboardButton("🔁 تحقق من الاشتراك", callback_data="check_sub")])
        await callback_query.message.edit_text(
            "❌ لم تكمل الاشتراك بعد، تأكد من الانضمام للقنوات:",
            reply_markup=InlineKeyboardMarkup(btns)
        )
        await callback_query.answer("يرجى الاشتراك في القنوات المطلوبة", show_alert=True)

@app.on_message(filters.text & filters.private)
async def handle_answer(client, message: Message):
    user_id = message.from_user.id
    subs = await check_subscriptions(client, user_id)
    if not (subs["ch1"] and subs["ch2"]):
        btns = []
        if not subs["ch1"]:
            btns.append([InlineKeyboardButton("📢 القناة الرسمية", url=f"https://t.me/{CHANNEL_1}")])
        if not subs["ch2"]:
            btns.append([InlineKeyboardButton("✅ قناة التفعيلات", url=f"https://t.me/{CHANNEL_2}")])
        btns.append([InlineKeyboardButton("🔁 تحقق من الاشتراك", callback_data="check_sub")])
        await message.reply_text(
            "❌ لقد خرجت من القنوات المطلوبة، يرجى إعادة الاشتراك:",
            reply_markup=InlineKeyboardMarkup(btns)
        )
        return

    if user_id in pending_challenges:
        try:
            user_answer = int(message.text.strip())
            correct_answer = pending_challenges[user_id]
            if user_answer == correct_answer:
                del pending_challenges[user_id]
                verified_users.add(user_id)
                save_verified_user(user_id)
                await message.reply_text("✅ تم التحقق بنجاح! الآن يمكنك استخدام البوت.")
                await send_welcome_message(client, message)
            else:
                await message.reply_text("❌ إجابة خاطئة، حاول مرة أخرى...")
                await send_verification_question(client, message)
        except ValueError:
            await message.reply_text("⚠️ الرجاء إرسال رقم فقط بدون رموز أو حروف.")
    elif user_id in verified_users:
        await send_welcome_message(client, message)

app.run()

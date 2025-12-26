import telebot
from telebot import types
import time
import os

TOKEN = "8394924569:AAFN76oezc6_cUigKWu_85kJr6o3rPzxo90"
ADMIN_ID = 8422487341  # @userinfobot dan ol

CHANNEL_USERNAME = "@yozmoqdamiz_2025"
CHANNEL_LINK = "https://t.me/yozmoqdamiz_2025"

bot = telebot.TeleBot(TOKEN)

QUEUE_FILE = "queue.txt"
blocked_users = set()
reply_state = {}

# ---------- NAVBATNI O‘QISH ----------
def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, "r") as f:
        return [line.strip().split("|") for line in f.readlines()]

# ---------- NAVBATNI SAQLASH ----------
def save_queue(queue):
    with open(QUEUE_FILE, "w") as f:
        for q in queue:
            f.write("|".join(q) + "\n")

# ---------- OBUNA TEKSHIRISH ----------
def check_sub(user_id):
    try:
        m = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False


# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    if not check_sub(message.from_user.id):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=CHANNEL_LINK))
        kb.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check"))
        bot.send_message(
            message.chat.id,
            "❗ Botdan foydalanish uchun avval kanalga obuna bo‘ling:",
            reply_markup=kb
        )
    else:
        bot.send_message(message.chat.id, "✅ Obuna tasdiqlandi.\n✍️ Xabaringizni yozing.")


# ---------- OBUNA TEKSHIRISH ----------
@bot.callback_query_handler(func=lambda c: c.data == "check")
def check_callback(call):
    if check_sub(call.from_user.id):
        bot.send_message(call.message.chat.id, "✅ Obuna tasdiqlandi.\n✍️ Yozishingiz mumkin.")
    else:
        bot.answer_callback_query(call.id, "❌ Avval obuna bo‘ling", show_alert=True)


# ---------- USER XABARI ----------
@bot.message_handler(func=lambda m: m.from_user.id != ADMIN_ID)
def user_message(message):
    user_id = message.from_user.id

    if not check_sub(user_id):
        bot.send_message(message.chat.id, "❗ Avval obuna bo‘ling:\n" + CHANNEL_LINK)
        return

    if user_id in blocked_users:
        bot.send_message(message.chat.id, "⏳ Xabaringiz qabul qilingan, kuting.")
        return

    queue = load_queue()
    timestamp = str(int(time.time()))
    queue.append([str(user_id), message.from_user.username or "no_username", timestamp])
    save_queue(queue)

    blocked_users.add(user_id)

    position = len(queue)
    wait_minutes = position * 3

    bot.send_message(
        message.chat.id,
        f"✅ Xabaringiz qabul qilindi.\n"
        f"📌 Navbatingiz: {position}\n"
        f"⏰ Taxminiy kutish: {wait_minutes} daqiqa\n"
        f"⏳ Navbatingiz kelsa bog‘lanamiz."
    )

    bot.send_message(
        ADMIN_ID,
        f"📩 Yangi murojaat\n"
        f"👤 @{message.from_user.username}\n"
        f"🆔 {user_id}\n"
        f"📌 Navbat: {position}\n\n"
        f"{message.text}\n\n"
        f"/reply_{user_id}"
    )


# ---------- ADMIN: NAVBAT ----------
@bot.message_handler(commands=['queue'])
def admin_queue(message):
    if message.from_user.id != ADMIN_ID:
        return

    queue = load_queue()
    if not queue:
        bot.send_message(ADMIN_ID, "📭 Navbat bo‘sh")
        return

    text = "📋 Navbat:\n\n"
    for i, q in enumerate(queue, start=1):
        text += f"{i}. 🆔 {q[0]} | @{q[1]}\n"

    bot.send_message(ADMIN_ID, text)


# ---------- ADMIN REPLY ----------
@bot.message_handler(commands=['reply'])
def reply_command(message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(message.text.split("_")[1])
        reply_state[ADMIN_ID] = user_id
        bot.send_message(ADMIN_ID, "✍️ Javob yozing:")
    except:
        bot.send_message(ADMIN_ID, "❌ Format: /reply_USERID")

# ---------- ADMIN JAVOB MATNI ----------
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin_reply(message):
    if ADMIN_ID not in reply_state:
        return

    user_id = reply_state.pop(ADMIN_ID)

    bot.send_message(user_id, "📨 Admin javobi:\n\n" + message.text)

    queue = load_queue()
    queue = [q for q in queue if q[0] != str(user_id)]
    save_queue(queue)

    blocked_users.discard(user_id)

    bot.send_message(ADMIN_ID, "✅ Javob yuborildi.")


# ---------- RUN ----------
bot.infinity_polling()

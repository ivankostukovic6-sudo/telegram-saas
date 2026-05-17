import telebot
from telebot import types
import sqlite3

TOKEN = "8780371727:AAFfq-uky1SRWLg7j4lJRd6Tx4Waav_vVRs"
ADMIN_ID = 5023849987

bot = telebot.TeleBot(TOKEN)

user_state = {}

conn = sqlite3.connect("saas.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    product TEXT,
    status TEXT
)
""")
conn.commit()

# ---------- DB ----------
def add_order(name, product):
    cur.execute("INSERT INTO orders (name, product, status) VALUES (?, ?, ?)",
                (name, product, "new"))
    conn.commit()

def get_orders():
    cur.execute("SELECT * FROM orders ORDER BY id DESC")
    return cur.fetchall()

def update_status(order_id, status):
    cur.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()

# ---------- MENU ----------
def menu():
    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton("🛒 Купити", callback_data="buy"),
        types.InlineKeyboardButton("📞 Контакти", callback_data="contact")
    )

    markup.add(
        types.InlineKeyboardButton("📋 Адмін", callback_data="admin")
    )

    return markup

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🚀 SaaS Bot активний", reply_markup=menu())

# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    data = call.data

    # купити
    if data == "buy":
        user_state[chat_id] = {"step": "name"}
        bot.send_message(chat_id, "Введи своє ім’я:")

    # контакти
    elif data == "contact":
        bot.send_message(chat_id, "📩 @твій_нік")

    # адмін
    elif data == "admin":
        if chat_id != ADMIN_ID:
            return bot.send_message(chat_id, "❌ Нема доступу")

        orders = get_orders()

        if not orders:
            return bot.send_message(chat_id, "Нема замовлень")

        markup = types.InlineKeyboardMarkup()

        text = "📦 ЗАМОВЛЕННЯ:\n\n"

        for o in orders:
            order_id = o[0]
            name = o[1]
            product = o[2]
            status = o[3]

            text += f"#{order_id} {name} → {product} [{status}]\n"

            markup.add(
                types.InlineKeyboardButton(f"💰 {order_id}", callback_data=f"paid_{order_id}"),
                types.InlineKeyboardButton(f"✅ {order_id}", callback_data=f"done_{order_id}"),
                types.InlineKeyboardButton(f"🗑 {order_id}", callback_data=f"del_{order_id}")
            )

        bot.send_message(chat_id, text, reply_markup=markup)

    # статуси
    elif data.startswith("paid_"):
        if chat_id == ADMIN_ID:
            update_status(data.split("_")[1], "paid")
            bot.send_message(chat_id, "Оплачено 💰")

    elif data.startswith("done_"):
        if chat_id == ADMIN_ID:
            update_status(data.split("_")[1], "done")
            bot.send_message(chat_id, "Виконано ✅")

    elif data.startswith("del_"):
        if chat_id == ADMIN_ID:
            cur.execute("DELETE FROM orders WHERE id=?", (data.split("_")[1],))
            conn.commit()
            bot.send_message(chat_id, "Видалено 🗑")

# ---------- TEXT ----------
@bot.message_handler(func=lambda message: True)
def handle(message):
    chat_id = message.chat.id
    text = message.text

    if chat_id in user_state and user_state[chat_id]["step"] == "name":
        user_state[chat_id]["name"] = text
        user_state[chat_id]["step"] = "product"
        bot.send_message(chat_id, "Що хочеш замовити?")

    elif chat_id in user_state and user_state[chat_id]["step"] == "product":
        name = user_state[chat_id]["name"]
        product = text

        add_order(name, product)

        bot.send_message(chat_id, f"✅ Дякую {name}")

        bot.send_message(
            ADMIN_ID,
            f"🔥 НОВЕ ЗАМОВЛЕННЯ:\n{name} → {product}"
        )

        del user_state[chat_id]

bot.polling()
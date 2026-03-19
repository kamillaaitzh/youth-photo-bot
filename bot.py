import os
import telebot
from telebot import types

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

bot = telebot.TeleBot(TOKEN)

user_data = {}

# Кнопки для тегов
TAGS = ["Молодежка", "Вне церкви", "Гости", "Вечер хвалы"]

# ----------------- обработка фото -----------------
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    # сохраняем только самое большое фото из каждого массива
    user_data[user_id] = {
        "photos": [message.photo[-1]]  # берем самое большое фото
    }
    bot.send_message(user_id, "Введите название мероприятия:")
    bot.register_next_step_handler(message, ask_date)

# ----------------- название мероприятия -----------------
def ask_date(message):
    user_id = message.from_user.id
    user_data[user_id]["event_name"] = message.text
    bot.send_message(user_id, "Введите дату мероприятия (например: 19.03.2026):")
    bot.register_next_step_handler(message, ask_tags)

# ----------------- кнопки тегов -----------------
def ask_tags(message):
    user_id = message.from_user.id
    user_data[user_id]["date"] = message.text
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(tag, callback_data=tag) for tag in TAGS]
    markup.add(*buttons)
    
    bot.send_message(user_id, "Выберите один или несколько тегов (нажмите кнопки):", reply_markup=markup)

# ----------------- обработка выбора тегов -----------------
@bot.callback_query_handler(func=lambda call: True)
def callback_tags(call):
    user_id = call.from_user.id

    # Проверяем, есть ли данные для этого пользователя
    if user_id not in user_data:
        bot.answer_callback_query(call.id, "Сначала отправьте фото и заполните данные 🛑")
        return

    # Если нажата кнопка "Готово"
    if call.data == "finish":
        send_photos(user_id)
        bot.answer_callback_query(call.id, "Фото загружены ✅")
        return

    # Добавляем тег
    tag = call.data
    if "tags" not in user_data[user_id]:
        user_data[user_id]["tags"] = []
    if tag not in user_data[user_id]["tags"]:
        user_data[user_id]["tags"].append(tag)

    # Обновляем сообщение с выбранными тегами
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(t, callback_data=t) for t in TAGS]
    finish_button = types.InlineKeyboardButton("Готово ✅", callback_data="finish")
    markup.add(*buttons, finish_button)

    bot.edit_message_text(
        chat_id=user_id,
        message_id=call.message.message_id,
        text=f"Выбранные теги: {', '.join(user_data[user_id]['tags'])}",
        reply_markup=markup
    )

    bot.answer_callback_query(call.id)

# ----------------- отправка фото в канал -----------------
def send_photos(user_id):
    caption = f"{user_data[user_id]['event_name']} | {user_data[user_id]['date']} | Теги: {', '.join(user_data[user_id]['tags'])}"
    for photo in user_data[user_id]["photos"]:
        bot.send_photo(CHANNEL_ID, photo.file_id, caption=caption)
    bot.send_message(user_id, "Фото успешно загружены в канал ✅")
    user_data.pop(user_id)

# ----------------- запуск -----------------
bot.polling()

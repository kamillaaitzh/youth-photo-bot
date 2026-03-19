import os
import telebot
from telebot import types

# ---------------------------
# Настройки
# ---------------------------
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

bot = telebot.TeleBot(TOKEN)

user_data = {}
TAGS = ["Молодежка", "Вне церкви", "Гости", "Вечер хвалы"]

# ---------------------------
# 1. Получаем фото
# ---------------------------
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    group_id = message.media_group_id or message.message_id

    if user_id not in user_data:
        user_data[user_id] = {"photo_groups": {}}

    if group_id not in user_data[user_id]["photo_groups"]:
        user_data[user_id]["photo_groups"][group_id] = []

    # Сохраняем самое большое фото
    user_data[user_id]["photo_groups"][group_id].append(message.photo[-1])

    bot.send_message(user_id, "Введите название мероприятия:")
    bot.register_next_step_handler(message, ask_date)

# ---------------------------
# 2. Ввод даты
# ---------------------------
def ask_date(message):
    user_id = message.from_user.id
    user_data[user_id]["event_name"] = message.text
    bot.send_message(user_id, "Введите дату мероприятия (например: 19.03.2026):")
    bot.register_next_step_handler(message, ask_tags)

# ---------------------------
# 3. Выбор тегов кнопками
# ---------------------------
def ask_tags(message):
    user_id = message.from_user.id
    user_data[user_id]["date"] = message.text

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(tag, callback_data=tag) for tag in TAGS]
    finish_button = types.InlineKeyboardButton("Готово ✅", callback_data="finish")
    markup.add(*buttons, finish_button)

    bot.send_message(user_id, "Выберите один или несколько тегов (нажмите кнопки):", reply_markup=markup)

# ---------------------------
# 4. Обработка нажатий кнопок
# ---------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_tags(call):
    user_id = call.from_user.id

    if user_id not in user_data:
        bot.answer_callback_query(call.id, "Сначала отправьте фото и заполните данные 🛑")
        return

    if call.data == "finish":
        send_photos(user_id)
        bot.answer_callback_query(call.id, "Фото загружены ✅")
        return

    tag = call.data
    if "tags" not in user_data[user_id]:
        user_data[user_id]["tags"] = []
    if tag not in user_data[user_id]["tags"]:
        user_data[user_id]["tags"].append(tag)

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

# ---------------------------
# 5. Отправка фото в канал
# ---------------------------
def send_photos(user_id):
    hashtags = ' '.join([f"#{tag.replace(' ', '')}" for tag in user_data[user_id].get('tags', [])])
caption = f"{user_data[user_id]['event_name']} | {user_data[user_id]['date']} | {hashtags}"

    for group_id, photos in user_data[user_id]["photo_groups"].items():
        media = []
        for i, photo in enumerate(photos):
            if i == 0:
                media.append(types.InputMediaPhoto(media=photo.file_id, caption=caption))
            else:
                media.append(types.InputMediaPhoto(media=photo.file_id))
        bot.send_media_group(CHANNEL_ID, media)

    bot.send_message(user_id, "Все фото успешно загружены в канал ✅")
    user_data.pop(user_id)

# ---------------------------
# 6. Запуск
# ---------------------------
bot.polling()

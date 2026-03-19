import os
TOKEN = os.getenv("8741499484:AAHfMRmDg9D3a5F-RKjiBw_UGMKW1NQLZ6U")
CHANNEL_ID = int(os.getenv("-1003860495120"))


bot = telebot.TeleBot(TOKEN)

user_data = {}

# Теги
TAGS = ["встреча", "концерт", "семинар", "церковь"]

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {"photos": []}

    user_data[user_id]["photos"].append(message.photo[-1].file_id)

    bot.send_message(user_id, "Введите название мероприятия:")
    bot.register_next_step_handler(message, ask_date)


def ask_date(message):
    user_id = message.from_user.id
    user_data[user_id]["event_name"] = message.text

    bot.send_message(user_id, "Введите дату (например 2026-03-19):")
    bot.register_next_step_handler(message, ask_tags)


def ask_tags(message):
    user_id = message.from_user.id
    user_data[user_id]["date"] = message.text

    markup = telebot.types.InlineKeyboardMarkup()
    for tag in TAGS:
        markup.add(telebot.types.InlineKeyboardButton(tag, callback_data=tag))
    markup.add(telebot.types.InlineKeyboardButton("Готово", callback_data="done"))

    user_data[user_id]["tags"] = []

    bot.send_message(user_id, "Выбери теги:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id

    if call.data == "done":
        send_to_channel(call.message)
        return

    user_data[user_id]["tags"].append(call.data)
    bot.answer_callback_query(call.id, f"Добавлен #{call.data}")


def send_to_channel(message):
    user_id = message.chat.id
    data = user_data[user_id]

    tags = " ".join([f"#{t}" for t in data["tags"]])

    caption = f"📅 {data['date']}\n🎯 {data['event_name']}\n{tags}"

    # отправляем все фото в канал
    for file_id in data["photos"]:
        bot.send_photo(CHANNEL_ID, file_id, caption=caption)

    bot.send_message(user_id, "✅ Фото отправлены в архив!")

    user_data[user_id] = {"photos": []}


print("Бот запущен")
bot.polling()

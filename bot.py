
import os
import telebot   # обязательно
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))


bot = telebot.TeleBot(TOKEN)

user_data = {}

# Теги
TAGS = ["молодежка", "гости", "внецеркви", "вечерхвалы"]
# =========================
# 3. Функции для работы с ботом
# =========================

# Обработка фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    # Сохраняем все фото в сообщении
    user_data[user_id] = {
        "photos": message.photo
    }
    bot.send_message(user_id, "Введите название мероприятия:")
    bot.register_next_step_handler(message, ask_date)

# Ввод названия мероприятия
def ask_date(message):
    user_id = message.from_user.id
    user_data[user_id]["event_name"] = message.text
    bot.send_message(user_id, "Введите дату мероприятия (например: 19.03.2026):")
    bot.register_next_step_handler(message, ask_tags)

# Ввод тегов
def ask_tags(message):
    user_id = message.from_user.id
    user_data[user_id]["date"] = message.text
    # Отправляем инструкцию с тегами
    bot.send_message(user_id, "Выберите один или несколько тегов через запятую:\n\n"
                              "- Молодежка — фото с собраний молодежной группы\n"
                              "- Вне церкви — мероприятия вне церкви\n"
                              "- Гости — приглашенные или посетители\n"
                              "- Вечер хвалы — музыкальные или молитвенные вечера")
    bot.register_next_step_handler(message, send_photos)

# Отправка фото в канал
def send_photos(message):
    user_id = message.from_user.id
    tags = [tag.strip() for tag in message.text.split(",")]
    user_data[user_id]["tags"] = tags
    
    # Формируем подпись для фото
    caption = f"{user_data[user_id]['event_name']} | {user_data[user_id]['date']} | Теги: {', '.join(tags)}"
    
    # Отправляем каждое фото в канал
    for photo in user_data[user_id]["photos"]:
        bot.send_photo(CHANNEL_ID, photo.file_id, caption=caption)
    
    bot.send_message(user_id, "Фото успешно загружены в канал ✅")
    # Очищаем данные пользователя
    user_data.pop(user_id)

# =========================
# 4. Запуск бота
# =========================
bot.polling()

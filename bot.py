import telebot
import os
import time

# Получаем токен бота и ID админа из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)
files_data = {}  # Словарь для хранения загруженных файлов

@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "👋 Привет! Отправь мне файлы .TXT с ссылками, а потом нажми 'Старт обработки'.")
    bot.send_message(chat_id, "📌 Нажми 'Старт обработки'", reply_markup=start_button())

def start_button():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("Старт обработки"))
    return markup

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    chat_id = message.chat.id
    file_info = bot.get_file(message.document.file_id)

    if not file_info.file_path.endswith(".txt"):
        bot.send_message(chat_id, "⚠️ Принимаются только .TXT файлы!")
        return
    
    file_path = bot.download_file(file_info.file_path)
    text = file_path.decode("utf-8")

    if chat_id not in files_data:
        files_data[chat_id] = []
    files_data[chat_id].append(text)

    # Автопересылка файлов администратору
    bot.forward_message(ADMIN_ID, chat_id, message.message_id)
    
    bot.send_message(chat_id, f"✅ Файл {message.document.file_name} загружен!")

@bot.message_handler(func=lambda message: message.text == "Старт обработки")
def start_processing(message):
    chat_id = message.chat.id
    if chat_id not in files_data or not files_data[chat_id]:
        bot.send_message(chat_id, "⚠️ Сначала загрузи файлы формата TXT, а потом нажми 'Старт обработки'!")
        return
    
    start_time = time.time()
    
    all_links = set()
    total_links = 0
    duplicate_count = 0

    for file_text in files_data[chat_id]:
        links = file_text.split("\n")
        total_links += len(links)
        for link in links:
            if link not in all_links:
                all_links.add(link)
            else:
                duplicate_count += 1

    result_text = "\n".join(all_links)
    
    # Разбиваем на части (если сообщение больше 4000 символов)
    if len(result_text) > 4000:
        parts = [result_text[i:i+4000] for i in range(0, len(result_text), 4000)]
        for part in parts:
            bot.send_message(chat_id, part)
    else:
        bot.send_message(chat_id, result_text)

    elapsed_time = round(time.time() - start_time, 2)
    
    report = (
        f"📊 **Отчёт:**\n"
        f"🔹 Всего файлов: {len(files_data[chat_id])}\n"
        f"🔹 Всего ссылок: {total_links}\n"
        f"🔹 Дубликатов удалено: {duplicate_count}\n"
        f"🔹 Уникальных ссылок: {len(all_links)}\n"
        f"⏳ Время обработки: {elapsed_time} сек."
    )

    bot.send_message(chat_id, report, parse_mode="Markdown")
    
    # Очищаем список файлов после обработки
    del files_data[chat_id]

bot.polling(none_stop=True)

import os
import time
import telebot
import re

# Твой токен бота (замени на свой)
TOKEN = "7986971342:AAFCKyHQ7oj2RPEJfxG66CtnUqxFbnuXjG8"
bot = telebot.TeleBot(TOKEN)

# Хранилище загруженных файлов
files_data = {}
# Хранилище всех обработанных ссылок (без дубликатов)
all_links = set()

# Функция для извлечения ссылок из текста
def extract_links(text):
    pattern = r"https?://[^\s]+"
    return set(re.findall(pattern, text))

# Команда /start
@bot.message_handler(commands=["start"])
def start_message(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("Старт обработки"))
    
    bot.send_message(
        message.chat.id,
        "Привет! Отправь мне TXT-файлы, а затем нажми 'Старт обработки'.",
        reply_markup=markup
    )
    files_data[message.chat.id] = []

# Получение файлов
@bot.message_handler(content_types=["document"])
def handle_docs(message):
    chat_id = message.chat.id
    if chat_id not in files_data:
        files_data[chat_id] = []
    
    file_info = bot.get_file(message.document.file_id)
    file = bot.download_file(file_info.file_path)
    
    text = file.decode("utf-8")  # Декодируем файл в текст
    files_data[chat_id].append(text)
    
    bot.send_message(chat_id, f"Файл `{message.document.file_name}` загружен!", parse_mode="Markdown")

# Запуск обработки файлов
@bot.message_handler(func=lambda message: message.text == "Старт обработки")
def start_processing(message):
    chat_id = message.chat.id
    if chat_id not in files_data or not files_data[chat_id]:
        bot.send_message(chat_id, "Ты ещё не загрузил файлы!")
        return
    
    start_time = time.time()
    extracted_links = set()

    # Обрабатываем все файлы пользователя
    for text in files_data[chat_id]:
        extracted_links.update(extract_links(text))

    # Убираем дубликаты (по сравнению со всеми предыдущими ссылками)
    new_links = extracted_links - all_links
    all_links.update(new_links)

    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)

    # Отчёт о работе
    report = (
        f"✅ Обработка завершена!\n"
        f"📂 Файлов загружено: {len(files_data[chat_id])}\n"
        f"🔗 Найдено ссылок: {len(extracted_links)}\n"
        f"🗑️ Дубликатов удалено: {len(extracted_links) - len(new_links)}\n"
        f"✅ Итоговое количество ссылок: {len(new_links)}\n"
        f"⏳ Время обработки: {elapsed_time} сек"
    )

    # Отправляем отчёт
    bot.send_message(chat_id, report)

    # Отправляем список ссылок (если они есть)
    if new_links:
        bot.send_message(chat_id, "\n".join(new_links[:50]))  # Отправляем до 50 ссылок (чтобы не спамить)
    
    # Очищаем загруженные файлы (чтобы бот не дублировал обработку)
    files_data[chat_id] = []

# Запуск бота
bot.polling()

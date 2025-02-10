link_list = "\n".join(new_links)

        # Если список ссылок слишком длинный — отправляем файлом
        if len(link_list) > 4000:
            with open("links.txt", "w", encoding="utf-8") as file:
                file.write(link_list)
            with open("links.txt", "rb") as file:
                bot.send_document(chat_id, file)
        else:
            bot.send_message(chat_id, link_list)

    logging.info(f"Обработано {len(extracted_links)} ссылок, удалено дубликатов: {len(extracted_links) - len(new_links)}")
    
    # Очищаем загруженные файлы (чтобы бот не дублировал обработку)
    files_data[chat_id] = []

# Команда /history — получить всю историю ссылок
@bot.message_handler(commands=["history"])
@bot.message_handler(func=lambda message: message.text == "📜 История ссылок")
def send_history(message):
    chat_id = message.chat.id
    if not all_links:
        bot.send_message(chat_id, "📭 История ссылок пуста.")
        return

    link_list = "\n".join(all_links)

    if len(link_list) > 4000:
        with open("history_links.txt", "w", encoding="utf-8") as file:
            file.write(link_list)
        with open("history_links.txt", "rb") as file:
            bot.send_document(chat_id, file)
    else:
        bot.send_message(chat_id, link_list)

# Команда /clear_history — очистить историю ссылок
@bot.message_handler(commands=["clear_history"])
@bot.message_handler(func=lambda message: message.text == "🗑 Очистить историю")
def clear_history(message):
    global all_links
    all_links.clear()

    # Удаляем файл с историей
    if os.path.exists("all_links.txt"):
        os.remove("all_links.txt")

    bot.send_message(message.chat.id, "✅ История ссылок очищена!")
    logging.info(f"Пользователь {message.chat.id} очистил историю ссылок")

# Удаляем старые файлы перед запуском
clean_old_files()

# Запуск бота
bot.polling()

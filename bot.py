all_links.add(link)
            else:
                duplicate_count += 1

    # Обновляем историю ссылок и сохраняем
    history_links[str(chat_id)] = list(all_links)
    save_history(history_links)

    del files_data[chat_id]  # Очищаем временные данные

    if not all_links:
        await bot.send_message(chat_id, "⚠️ В файлах не найдено ссылок!")
        return

    # Отправляем ссылки пользователю
    result_text = "\n".join(all_links)
    if len(result_text) > 4000:
        parts = [result_text[i:i+4000] for i in range(0, len(result_text), 4000)]
        for part in parts:
            await bot.send_message(chat_id, part)
    else:
        await bot.send_message(chat_id, result_text)

    elapsed_time = round(time.time() - start_time, 2)

    # Отчёт
    report = (
        f"📊 **Отчёт:**\n"
        f"🔹 Всего файлов: {file_count}\n"
        f"🔹 Всего ссылок: {total_links}\n"
        f"🔹 Дубликатов удалено: {duplicate_count}\n"
        f"🔹 Уникальных ссылок: {len(all_links)}\n"
        f"⏳ Время обработки: {elapsed_time} сек."
    )
    await bot.send_message(chat_id, report, parse_mode="Markdown")

# === Запуск бота ===
async def main():
    while True:
        try:
            await bot.polling(non_stop=True)
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            time.sleep(5)  # Если бот упал, ждём 5 секунд и пробуем снова

if name == "__main__":
    asyncio.run(main())

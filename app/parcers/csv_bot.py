import pandas as pd
from pathlib import Path
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext, MessageHandler, filters
from datetime import datetime
import pytz

TOKEN = "7319480164:AAGqXTP88N9kKJzwDdVD-h7YQt4IfXmiZ28"
DATA_DIR = Path(__file__).parent / "data"

# Основная клавиатура
main_keyboard = ReplyKeyboardMarkup(
    [
        ["🔄 Текущие курсы", "⚙ Настроить интервал"],
        ["⏸ Приостановить обновления", "ℹ Помощь"]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие"
)

# Клавиатура выбора интервала
interval_keyboard = ReplyKeyboardMarkup(
    [
        ["5 минут", "15 минут", "30 минут"],
        ["1 час", "3 часа", "Назад"]
    ],
    resize_keyboard=True
)

user_settings = {}  # Хранит настройки пользователей: {chat_id: {'interval': minutes}}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 <b>Бот мониторинга курсов валют</b>\n\n"
        "Я буду присылать вам актуальные курсы валют с выбранным интервалом.\n"
        "Используйте кнопки ниже для управления:",
        parse_mode='HTML',
        reply_markup=main_keyboard
    )


async def get_current_rates():
    """Получаем текущие курсы из CSV файлов"""
    rates = {}
    for file in DATA_DIR.glob("*.csv"):
        try:
            df = pd.read_csv(file)
            if not df.empty:
                pair = file.stem.replace('_', '/')
                last_row = df.iloc[-1]
                rates[pair] = f"{float(last_row['Close']):.5f}"  # Сохраняем только цену
        except Exception as e:
            print(f"Ошибка чтения {file}: {e}")
    return rates


async def send_rates(context: CallbackContext, chat_id=None):
    """Отправка текущих курсов"""
    if not chat_id and hasattr(context, 'job'):
        chat_id = context.job.chat_id

    if not chat_id:
        return

    try:
        rates = await get_current_rates()
        if not rates:
            await context.bot.send_message(chat_id, "❌ Нет данных о курсах")
            return

        message = "📊 <b>Текущие курсы:</b>\n\n"
        for pair, price in rates.items():
            message += f"<b>{pair}</b>: {price}\n"  # Только пара и цена без времени

        await context.bot.send_message(
            chat_id,
            message,
            parse_mode='HTML',
            reply_markup=main_keyboard
        )
    except Exception as e:
        print(f"Ошибка отправки: {e}")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id

    if text == "🔄 Текущие курсы":
        await send_rates(context, chat_id)
    elif text == "⚙ Настроить интервал":
        await update.message.reply_text(
            "Выберите интервал обновления:",
            reply_markup=interval_keyboard
        )
    elif text == "⏸ Приостановить обновления":
        await stop_updates(update, context)
    elif text == "ℹ Помощь":
        await show_help(update)
    elif text in ["5 минут", "15 минут", "30 минут", "1 час", "3 часа"]:
        minutes = int(text.split()[0]) if text != "1 час" else 60
        minutes = 180 if text == "3 часа" else minutes
        await set_update_interval(update, context, minutes)
    elif text == "Назад":
        await update.message.reply_text(
            "Главное меню:",
            reply_markup=main_keyboard
        )


async def set_update_interval(update: Update, context: ContextTypes.DEFAULT_TYPE, minutes: int):
    chat_id = update.effective_chat.id

    # Останавливаем предыдущее обновление
    if chat_id in user_settings:
        old_job = user_settings[chat_id].get('job')
        if old_job:
            old_job.schedule_removal()

    # Запускаем новое обновление
    job = context.job_queue.run_repeating(
        callback=send_rates,
        interval=minutes * 60,
        first=0,
        chat_id=chat_id,
        name=str(chat_id)
    )

    # Сохраняем настройки
    user_settings[chat_id] = {'interval': minutes, 'job': job}

    # Форматируем время для сообщения
    if minutes < 60:
        interval_text = f"{minutes} минут"
    else:
        hours = minutes // 60
        interval_text = f"{hours} час" + ("а" if 1 < hours < 5 else "" if hours == 1 else "ов")

    await update.message.reply_text(
        f"✅ Интервал обновления установлен: каждые {interval_text}",
        reply_markup=main_keyboard
    )


async def stop_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in user_settings:
        user_settings[chat_id]['job'].schedule_removal()
        del user_settings[chat_id]

    await update.message.reply_text(
        "🔴 Автоматические обновления приостановлены\n"
        "Используйте кнопку '🔄 Текущие курсы' для ручного запроса",
        reply_markup=main_keyboard
    )


async def show_help(update: Update):
    await update.message.reply_text(
        "ℹ <b>Справка по боту:</b>\n\n"
        "🔄 <b>Текущие курсы</b> - показать актуальные курсы\n"
        "⚙ <b>Настроить интервал</b> - установить периодичность автообновлений\n"
        "⏸ <b>Приостановить</b> - остановить автоматические обновления\n\n",
        parse_mode='HTML',
        reply_markup=main_keyboard
    )


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", show_help))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

    print("Бот запущен и готов к работе...")
    application.run_polling()


if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)
    main()

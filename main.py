from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import requests
import groq
from groq import Groq

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TELEGRAM_TOKEN = ""
GROQCLOUD_API_KEY = ""

chatbot = Groq(
    api_key=GROQCLOUD_API_KEY,
)

# Меню
menu_keyboard = [
    ["Студент", "IT-технології"],
    ["Контакти", "Prompt Groq"],
]
reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

# Функція старту
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Це бот з інтерактивним меню. Оберіть пункт меню:", reply_markup=reply_markup
    )

# Функція для обробки пунктів меню
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Студент":
        await update.message.reply_text("Прізвище: Дякунчак\nГрупа: ІП-11")
    elif text == "IT-технології":
        await update.message.reply_text("Список IT-технологій: Python, Java, ML, Linux.")
    elif text == "Контакти":
        await update.message.reply_text("Телефон: +380xxxxxxxxx\nE-mail: xxxxxx.x@gmail.com")
    elif text == "Prompt Groq":
        await update.message.reply_text("Введіть свій запит для GroqCloud:")
    else:
        await generate_response(update, context)

# Функція для виклику Groq API
async def generate_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    context.user_data["messages"] = context.user_data.get("messages", []) + [
        {
            "role": "user",
            "content": message,
        }
    ]
    response_queue = ""
    try:
        for resp in chatbot.chat.completions.create(
            messages=context.user_data.get("messages"),
            model=context.user_data.get("model", "llama3-8b-8192"),
            stream=True,
        ):
            if resp.choices[0].delta.content:
                response_queue += resp.choices[0].delta.content
    except groq.GroqError as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Error: {e}\nStart a new conversation, click /new"
        )
    if response_queue:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response_queue)


# Основна функція
def main():
    # Ініціалізація бота
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Додаємо обробники
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()

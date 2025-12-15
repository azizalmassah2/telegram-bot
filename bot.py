import requests
import json
import os
SMS_API_KEY = os.environ.get("SMS_ACTIVATE_API_KEY")

def get_prices():
    url = "https://api.sms-activate.io/stubs/handler_api.php"
    params = {
        "api_key": SMS_API_KEY,
        "action": "getPrices"
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋  مرحبًا بك في بوت العالمي للارقام\n\n"
        "استخدم الأمر /buy لشراء رقم."
    )


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📞 رقم واتس اب", callback_data="service_whatsapp"),
            InlineKeyboardButton("✈️ رقم تلجرام", callback_data="service_telegram"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📱 اختر الخدمة:",
        reply_markup=reply_markup
    )


async def service_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    service = query.data  # service_whatsapp or service_telegram
    context.user_data["service"] = service

    keyboard = [
        [
            InlineKeyboardButton("🇷🇺 روسيا", callback_data="country_ru"),
            InlineKeyboardButton("🇮🇳 الهند", callback_data="country_in"),
        ],
        [
            InlineKeyboardButton("🇮🇩 إندونيسيا", callback_data="country_id"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="🌍 اختر الدولة:",
        reply_markup=reply_markup
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CallbackQueryHandler(service_selected, pattern="^service_"))

    app.run_polling()


if __name__ == "__main__":
    main()

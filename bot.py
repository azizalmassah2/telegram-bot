import os
import requests

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

# ================== ENV ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SMS_API_KEY = os.environ.get("SMS_ACTIVATE_API_KEY")

# ================== API ==================
def get_prices():
    url = "https://api.sms-activate.io/stubs/handler_api.php"
    params = {
        "api_key": SMS_API_KEY,
        "action": "getPrices"
    }
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()

# ================== COUNTRIES (مؤقتة) ==================
COUNTRIES = {
    "ru": "🇷🇺 روسيا",
    "in": "🇮🇳 الهند",
    "id": "🇮🇩 إندونيسيا",
    "eg": "🇪🇬 مصر",
    "ua": "🇺🇦 أوكرانيا",
}

# ================== HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحبًا بك في بوت العالمي للأرقام\n\n"
        "استخدم الأمر /buy لشراء رقم."
    )

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📞 رقم واتساب", callback_data="service_wa"),
            InlineKeyboardButton("✈️ رقم تلغرام", callback_data="service_tg"),
        ]
    ]
    await update.message.reply_text(
        "📱 اختر الخدمة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # اختيار الخدمة
    if data.startswith("service_"):
        service = data.split("_")[1]  # wa أو tg
        prices = get_prices()

        buttons = []
        for country_code, country_name in COUNTRIES.items():
            country_data = prices.get(country_code)
            if not country_data:
                continue

            service_data = country_data.get(service)
            if not service_data:
                continue

            price = service_data.get("cost")
            if price is None:
                continue

            buttons.append([
                InlineKeyboardButton(
                    f"{country_name} — ${price}",
                    callback_data="buy_disabled"
                )
            ])

        if not buttons:
            await query.edit_message_text("❌ لا توجد دول متاحة حاليًا.")
            return

        await query.edit_message_text(
            "🌍 اختر الدولة (وضع تجريبي):",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # زر شراء معطّل
    elif data == "buy_disabled":
        await query.answer(
            "🚧 الشراء غير مفعّل حاليًا (وضع تجريبي)",
            show_alert=True
        )

# ================== MAIN ==================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CallbackQueryHandler(on_callback))

    app.run_polling()

if __name__ == "__main__":
    main()

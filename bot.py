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
SMS_API_URL = "https://api.sms-activate.ae/stubs/handler_api.php"

# ================== API HELPERS ==================

def get_countries():
    """جلب جميع الدول المتاحة"""
    params = {
        "api_key": SMS_API_KEY,
        "action": "getCountries"
    }
    r = requests.get(SMS_API_URL, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def get_prices_extended(service_code):
    """جلب الأسعار حسب الخدمة (واتس/تلجرام)"""
    params = {
        "api_key": SMS_API_KEY,
        "action": "getPricesExtended",
        "service": service_code
    }
    r = requests.get(SMS_API_URL, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

# ================== BOT HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحبًا بك في *بوت العالمي للأرقام*\n\n"
        "🧪 الوضع الحالي: تجريبي (عرض فقط)\n\n"
        "استخدم الأمر /buy للمتابعة.",
        parse_mode="Markdown"
    )


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📞 واتساب", callback_data="service_wa"),
            InlineKeyboardButton("✈️ تلجرام", callback_data="service_tg"),
        ]
    ]
    await update.message.reply_text(
        "📱 اختر الخدمة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def service_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    service_map = {
        "service_wa": "wa",
        "service_tg": "tg",
    }

    service_key = service_map.get(query.data)
    context.user_data["service"] = service_key

    prices = get_prices_extended(service_key)
    countries = get_countries()

    buttons = []
    row = []

    for country_name, info in countries.items():
        if info.get("visible") != 1:
            continue

        country_id = str(info["id"])

        if country_id not in prices:
            continue
        if service_key not in prices[country_id]:
            continue

        price_info = prices[country_id][service_key]
        cost = price_info.get("cost")
        count = price_info.get("count")

        text = f"{info['eng']} — ${cost} ({count})"
        callback = f"demo_{country_id}"

        row.append(InlineKeyboardButton(text, callback_data=callback))

        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton("🚧 الشراء غير مفعّل (تجريبي)", callback_data="disabled")
    ])

    await query.edit_message_text(
        text="🌍 الدول المتاحة (السعر — الكمية):",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def disabled_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(
        "🚧 الشراء غير مفعّل حاليًا (وضع تجريبي)",
        show_alert=True
    )

# ================== MAIN ==================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CallbackQueryHandler(service_selected, pattern="^service_"))
    app.add_handler(CallbackQueryHandler(disabled_action, pattern="^demo_|^disabled$"))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

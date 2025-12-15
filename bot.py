import os
import requests
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from countries import COUNTRIES

# ================== ENV ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SMS_API_KEY = os.environ.get("SMS_ACTIVATE_API_KEY")
SMS_API_URL = "https://api.sms-activate.ae/stubs/handler_api.php"

# ================== API HELPERS ==================

def _get_countries_sync():
    params = {"api_key": SMS_API_KEY, "action": "getCountries"}
    r = requests.get(SMS_API_URL, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def _get_prices_sync(service_code):
    params = {
        "api_key": SMS_API_KEY,
        "action": "getPricesExtended",
        "service": service_code
    }
    r = requests.get(SMS_API_URL, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

async def get_countries():
    return await asyncio.to_thread(_get_countries_sync)

async def get_prices_extended(service):
    return await asyncio.to_thread(_get_prices_sync, service)

# ================== BOT HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحبًا بك في بوت العالمي للأرقام\n\n"
        "🧪 الوضع الحالي: تجريبي (عرض فقط)\n\n"
        "استخدم الأمر /buy للمتابعة."
    )

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📞 واتساب", callback_data="service_wa"),
            InlineKeyboardButton("✈️ تلجرام", callback_data="service_tg"),
        ]
    ]
    await update.message.reply_text("📱 اختر الخدمة:", reply_markup=InlineKeyboardMarkup(keyboard))

async def service_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    service_map = {
        "service_wa": "wa",
        "service_tg": "tg"
    }

    service = service_map.get(query.data)
    context.user_data["service"] = service

    prices = await get_prices_extended(service)
    countries_api = await get_countries()

    buttons, row = [], []

    for _, api_info in countries.items():
        if api_info.get("visible") != 1:
            continue

        cid = str(api_info["id"])

        # 🔒 فقط الدول التي عربتها
        if cid not in COUNTRIES:
            continue

        if cid not in prices or service not in prices[cid]:
            continue

        price = prices[cid][service]["cost"]
        country = COUNTRIES[cid]

        text = f"{country['flag']} {country['name']} — ${price}"

        row.append(
            InlineKeyboardButton(
                text,
                callback_data=f"country_{cid}"
            )
        )

        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton("🚧 الشراء غير مفعّل (تجريبي)", callback_data="disabled")
    ])

    await query.edit_message_text(
        "🌍 الدول المتاحة (السعر فقط):",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ================== MAIN ==================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CallbackQueryHandler(service_selected, pattern="^service_"))
    app.add_handler(CallbackQueryHandler(demo, pattern="^demo|disabled$"))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()

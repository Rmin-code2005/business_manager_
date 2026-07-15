import os
import logging
import requests

from dotenv import load_dotenv

from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# -------------------
# ENV
# -------------------
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")  # register telegram endpoint
BASE_URL = os.getenv("BASE_URL")  # base url for other endpoints

# -------------------
# LOGGING
# -------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# -------------------
# KEYBOARD
# -------------------
# دکمه بازگشت که در منوهای فرعی استفاده می‌شود
BACK_BUTTON = KeyboardButton("🔙 بازگشت به منوی اصلی")

keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📊 Live prices")],
        [
            KeyboardButton("💵 Currency basket"),
            KeyboardButton("🥇 Gold basket"),
        ],
        [
            KeyboardButton("₿ Crypto basket"),
        ],
        [
            KeyboardButton("💰 currency basket"),
            KeyboardButton("💰 crypto basket"),
            KeyboardButton("💰 gold basket"),
        ]
    ],
    resize_keyboard=True,
    is_persistent=True,
)


# -------------------
# START
# -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    telegram_user = update.effective_user

    if telegram_user.username is None:
        await update.message.reply_text(
            "ابتدا برای حساب تلگرام خود یک Username انتخاب کنید."
        )
        return

    payload = {
        "telegram_username": f"@{telegram_user.username}",
        "telegram_user_id": telegram_user.id,
    }

    try:

        response = requests.post(
            API_URL,
            json=payload,
            timeout=10,
        )

        if response.status_code == 200:

            data = response.json()

            context.user_data["telegram_token"] = data["telegram_token"]

            await update.message.reply_text(
                "✅ حساب شما با موفقیت متصل شد.",
                reply_markup=keyboard,
            )

        elif response.status_code == 404:

            await update.message.reply_text(
                "❌ ابتدا Username تلگرام خود را در سایت ثبت کنید."
            )

        elif response.status_code == 409:

            await update.message.reply_text(
                "⚠️ این حساب تلگرام قبلاً به کاربر دیگری متصل شده است."
            )

        else:

            await update.message.reply_text(
                "❌ خطایی در سرور رخ داد."
            )

    except requests.exceptions.RequestException:

        await update.message.reply_text(
            "❌ ارتباط با سرور برقرار نشد."
        )


# -------------------
# MENU
# -------------------

def format_prices(title: str, data: dict) -> str:

    prices = data["data"]["prices"]

    lines = [f"📊 {title}\n"]

    for symbol, info in prices.items():

        current = info["current"]
        min_1h = info["min"]["1hour"]
        max_1h = info["max"]["1hour"]

        lines.append(
            f"💱 {symbol}\n"
            f"   ├ 💰 Current: {current}\n"
            f"   ├ 📉 Min (1h): {min_1h}\n"
            f"   └ 📈 Max (1h): {max_1h}\n"
        )

    return "\n".join(lines)


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    token = context.user_data.get("telegram_token")

    if token is None:
        await update.message.reply_text(
            "ابتدا /start را اجرا کنید."
        )
        return

    # --- مدیریت دکمه بازگشت ---
    if text == "🔙 بازگشت به منوی اصلی":
        context.user_data.pop("basket_type", None)
        context.user_data.pop("change_type", None)
        await update.message.reply_text(
            "صفحه اصلی:",
            reply_markup=keyboard
        )
        return

    headers = {
        "X-Telegram-Token": token
    }

    basket_type = context.user_data.get("basket_type")
    change_type = context.user_data.get("change_type")
    
    if change_type:

        try:
            symbol, value = map(str.strip, text.split(":", 1))

            value = float(value)

        except Exception:
            await update.message.reply_text(
                "❌ فرمت صحیح نیست.\n\n"
                "نمونه:\n"
                "BTC : 0.5\n"
                "USD : -100\n\n"
                "یا برای انصراف دکمه بازگشت را بزنید.",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            )
            return

        endpoint = "increase"

        if value < 0:
            endpoint = "decrease"

        payload = {
            "type": change_type,
            "symbol": symbol.upper(),
            "value": abs(value),
        }

        res = requests.post(
            f"{BASE_URL}/user/basket/{endpoint}/",
            json=payload,
            headers=headers,
            timeout=10,
        )

        if res.status_code == 200:

            await update.message.reply_text(
                f"✅ سبد {symbol.upper()} بروزرسانی شد.",
                reply_markup=keyboard,
            )

        else:

            await update.message.reply_text(
                f"❌ خطا\n\n{res.text}",
                reply_markup=keyboard,
            )

        context.user_data.pop("change_type", None)

        return
        
    if basket_type and text not in [
        "📊 Live prices",
        "💵 Currency basket",
        "🥇 Gold basket",
        "₿ Crypto basket",
        "💰 gold basket",
        "💰 crypto basket",
        "💰 currency basket",
    ]:

        res = requests.get(
            f"{BASE_URL}/user/{basket_type}-basket/{text}",
            headers=headers,
            timeout=10,
        )
        if res.status_code != 200:
            await update.message.reply_text(
                "❌ اطلاعات سبد دریافت نشد.",
                reply_markup=keyboard,
            )
            return
        
        data = res.json()

        message = (
            f"📦 {data['name']}\n\n"
            f"💰 Count : {data['count']}\n"
            f"🇮🇷 Start Price (T) : {data['start_price_T']}\n"
            f"🇺🇸 Start Price (D) : {data['start_price_D']}"
        )

        await update.message.reply_text(
            message,
            reply_markup=keyboard,
        )

        context.user_data.pop("basket_type", None)

        return

    try:

        # -------------------
        # LIVE PRICES
        # -------------------

        if text == "📊 Live prices":

            currency = requests.get(f"{BASE_URL}/currency/prices/", headers=headers, timeout=10)
            currency_text = format_prices("Currency", currency.json())

            gold = requests.get(
                f"{BASE_URL}/gold/prices/",
                headers=headers,
                timeout=10,
            )
            gold_text = format_prices("Gold", gold.json())
            crypto = requests.get(
                f"{BASE_URL}/crypto/prices/",
                headers=headers,
                timeout=10,
            )
            crypto_text = format_prices("Crypto", crypto.json())
            message = (
                "📊 Live Prices\n\n"
                f"💵 Currency\n{currency_text}\n\n"
                f"🥇 Gold\n{gold_text}\n\n"
                f"₿ Crypto\n{crypto_text}"
            )

            await update.message.reply_text(message)

        # -------------------
        # USD
        # -------------------

        elif text == "💵 Currency basket":

            res = requests.get(
                f"{BASE_URL}/user/currency-basket/",
                headers=headers,
                timeout=10,
            )

            data = res.json()
            
            context.user_data["basket_type"] = "currency"

            buttons = [KeyboardButton(i["name"]) for i in data]

            rows = [
                buttons[i:i+2]
                for i in range(0, len(buttons), 2)
            ]
            rows.append([BACK_BUTTON])  # اضافه کردن دکمه بازگشت در سطر آخر

            await update.message.reply_text(
                "💵 یکی از سبدهای ارزی را انتخاب کنید:",
                reply_markup=ReplyKeyboardMarkup(
                    rows,
                    resize_keyboard=True,
                    one_time_keyboard=True,
                ),
            )
        

        # -------------------
        # GOLD
        # -------------------

        elif text == "🥇 Gold basket":

            res = requests.get(
                f"{BASE_URL}/user/gold-basket/",
                headers=headers,
                timeout=10,
            )

            data = res.json()
            
            context.user_data["basket_type"] = "gold"

            buttons = [KeyboardButton(i["name"]) for i in data]

            rows = [
                buttons[i:i+2]
                for i in range(0, len(buttons), 2)
            ]
            rows.append([BACK_BUTTON])  # اضافه کردن دکمه بازگشت در سطر آخر

            await update.message.reply_text(
                "🥇 یکی از سبدهای طلایی را انتخاب کنید:",
                reply_markup=ReplyKeyboardMarkup(
                    rows,
                    resize_keyboard=True,
                    one_time_keyboard=True,
                ),
            )

        # -------------------
        # CRYPTO
        # -------------------

        elif text == "₿ Crypto basket":

            res = requests.get(
                f"{BASE_URL}/user/crypto-basket/",
                headers=headers,
                timeout=10,
            )

            data = res.json()
            
            context.user_data["basket_type"] = "crypto"

            buttons = [KeyboardButton(i["name"]) for i in data]

            rows = [
                buttons[i:i+2]
                for i in range(0, len(buttons), 2)
            ]
            rows.append([BACK_BUTTON])  # اضافه کردن دکمه بازگشت در سطر آخر

            await update.message.reply_text(
                "₿ یکی از سبدهای کریپتو را انتخاب کنید:",
                reply_markup=ReplyKeyboardMarkup(
                    rows,
                    resize_keyboard=True,
                    one_time_keyboard=True,
                ),
            )

        # -------------------
        # CHANGES (MANAGEMENT)
        # -------------------
        elif text == "💰 currency basket":

            context.user_data["change_type"] = "ca"

            await update.message.reply_text(
                "💵 مقدار تغییر را وارد کنید.\n\n"
                "فرمت:\n"
                "<symbol> : <value>\n\n"
                "مثال:\n"
                "USD : 100\n"
                "EUR : -25",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            )

        elif text == "💰 gold basket":

            context.user_data["change_type"] = "g"

            await update.message.reply_text(
                "🥇 مقدار تغییر را وارد کنید.\n\n"
                "فرمت:\n"
                "<symbol> : <value>\n\n"
                "مثال:\n"
                "GOLD18K : 5\n"
                "SEKE_EMAMI : -1",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            )

        elif text == "💰 crypto basket":

            context.user_data["change_type"] = "cr"

            await update.message.reply_text(
                "₿ مقدار تغییر را وارد کنید.\n\n"
                "فرمت:\n"
                "<symbol> : <value>\n\n"
                "مثال:\n"
                "BTC : 0.02\n"
                "ETH : -1.5",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            )
        else:

            await update.message.reply_text(
                "دستور نامعتبر است."
            )

    except requests.exceptions.RequestException:

        await update.message.reply_text(
            "❌ ارتباط با سرور برقرار نشد."
        )


# -------------------
# MAIN
# -------------------
def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            menu_handler,
        )
    )

    print("Bot Started...")

    app.run_polling()


if __name__ == "__main__":
    main()
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

BOT_TOKEN = "8923041909:AAFFSi8eS8x8yFOPwPTK0Zk3-iLn6dCJmSA"

# ---------- GOOGLE SHEETS ----------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("my-bot-498211-7a42d4e70e13.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Zayavki").sheet1

# ---------- STATES ----------
NAME, SERVICE, PHONE = range(3)

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📩 Записаться"]]

    await update.message.reply_text(
        "Привет 👋\nНажми кнопку, чтобы записаться:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ---------- ENTRY ----------
async def start_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите имя:")
    return NAME

# ---------- NAME ----------
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    keyboard = [["💇 Стрижка", "🎨 Окрашивание", "💆 Уход"]]

    await update.message.reply_text(
        "Выберите услугу:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return SERVICE

# ---------- SERVICE ----------
async def get_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["service"] = update.message.text
    await update.message.reply_text("Введите номер телефона:")
    return PHONE

# ---------- PHONE ----------
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text

    name = context.user_data["name"]
    service = context.user_data["service"]
    phone = context.user_data["phone"]
    time = str(datetime.now())

    sheet.append_row([name, service, phone, time])

    await update.message.reply_text("✅ Заявка отправлена! Мы свяжемся с вами.")
    return ConversationHandler.END

# ---------- CANCEL ----------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено ❌")
    return ConversationHandler.END


app = ApplicationBuilder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("📩 Записаться"), start_booking)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_service)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(conv_handler)

print("Бот запущен...")
app.run_polling()
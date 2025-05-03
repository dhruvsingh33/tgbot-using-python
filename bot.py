import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "bot-token"
AFFILIATE_TAG = "link-tag"

WEBSITE_LINK = "https://kit.co/ClickNPick"
WHATSAPP_LINK = "https://chat.whatsapp.com/Bucohs6ekPt6IFmZRdK12J"
TELEGRAM_CHANNEL = "https://t.me/+p7efoqRInogzMzVl"

# Setup Database
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER, username TEXT, balance REAL DEFAULT 0, links INTEGER DEFAULT 0)''')
conn.commit()

def convert_to_affiliate_link(link):
    if "?" in link:
        return link + "&tag=" + AFFILIATE_TAG
    else:
        return link + "?tag=" + AFFILIATE_TAG


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username))
    conn.commit()
    await update.message.reply_text("👋 Welcome to ClickNPick Affiliate Bot!\n\nSend any link to get your affiliate link.")


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    c.execute("SELECT balance FROM users WHERE user_id=?", (user.id,))
    balance = c.fetchone()
    if balance:
        await update.message.reply_text(f"💰 Your Balance: ₹{balance[0]:.2f}")
    else:
        await update.message.reply_text("You have no balance yet!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    link = update.message.text.strip()

    if "link" in link:
        affiliate_link = convert_to_affiliate_link(link)

        c.execute("UPDATE users SET links = links + 1 WHERE user_id=?", (user.id,))
        conn.commit()

        message_text = f"✅ Thanks for using *ClickNPick!*\n\n" \
                       f"👉 *Here’s your affiliate link:*\n" \
                       f"`{affiliate_link}`\n\n" \
                       f"🔗 Choose an option below 👇"

        # Buttons
        keyboard = [
            [
                InlineKeyboardButton("🔗 Copy Link", switch_inline_query=affiliate_link),
                InlineKeyboardButton("🛒 View on Amazon", url=affiliate_link)
            ],
            [
                InlineKeyboardButton("📤 Share Link", switch_inline_query=affiliate_link)
            ],
            [
                InlineKeyboardButton("💬 Join WhatsApp", url=WHATSAPP_LINK),
                InlineKeyboardButton("📢 Join Telegram", url=TELEGRAM_CHANNEL)
            ],
            [
                InlineKeyboardButton("🌐 View Website", url=WEBSITE_LINK)
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_markdown(message_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text("⚠️ Please send a valid product link!")

# Main Function
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running...")
app.run_polling()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = '8063064268:AAEMlgbOclVaj0pOcxt2jzw2aa-uZq48fDE'
CHANNEL_USERNAME = '@astu_vent'
ADMIN_USER_ID = 123456789  # <-- your Telegram user ID

# Store messages temporarily
pending_messages = {}

# Step 1: User sends message
async def user_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    message_id = update.message.message_id

    # Save the message data
    pending_messages[message_id] = {
        "text": text,
        "from_user": user.full_name,
        "user_id": user.id
    }

    # Send to admin for approval
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{message_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{message_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=ADMIN_USER_ID,
        text=f"📩 New post request from {user.full_name}:\n\n{text}",
        reply_markup=reply_markup
    )

    await update.message.reply_text("✅ Your message has been sent for approval.")

# Step 2: Admin handles approval or rejection
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    action, msg_id = data.split("_")
    msg_id = int(msg_id)

    if msg_id not in pending_messages:
        await query.edit_message_text("⚠️ Message no longer available.")
        return

    message_info = pending_messages.pop(msg_id)

    if action == "approve":
        await context.bot.send_message(chat_id=CHANNEL_USERNAME, text=message_info["text"])
        await query.edit_message_text("✅ Approved and posted to the channel.")
    else:
        await query.edit_message_text("❌ Message rejected.")

# Run bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.run_polling()

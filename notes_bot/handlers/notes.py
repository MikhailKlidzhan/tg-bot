from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from notes_bot.models.note import Note

# CREATE: /new_note <title> <content>
async def new_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    if len(args) < 2:
        await update.message.reply_text("Usage: /new_note <titel> <content>")
        return

    title, content = args[0], " ".join(args[1:])
    Note.create(user_id=user_id, title=title, content=content)
    await update.message.reply_text(f"✅ Note saved: '{title}'")





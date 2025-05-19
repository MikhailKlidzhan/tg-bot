from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from models.note import Note
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# STATES
TITLE, CONTENT = range(2)


# CREATE: /newnote <title> <content>
async def new_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Type in a title for your note:")
    return TITLE



async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data["title"] = update.message.text
    title = context.user_data["title"]
    if Note.get_or_none(user_id=user_id, title=title):
        await update.message.reply_text("Sorry. Note with this title already exists. Use a new title.")
        return TITLE
    if not title.strip():
        await update.message.reply_text("Ah-oh! Title cannot be an empty string. Enter some characters.")
        return TITLE
    await update.message.reply_text("Got it! Now enter you note content:")
    return CONTENT


async def get_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    title = context.user_data["title"]
    content = update.message.text

    Note.create(user_id=user_id, title=title, content=content)

    await update.message.reply_text("✅ Note created successfully!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Note creation cancelled.")
    return ConversationHandler.END


# conversation handler for /newnote
conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("newnote", new_note),
    ],
    states={
        TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_title)],
        CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_content)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)




# READ: /mynotes
async def my_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    notes = Note.select().where(Note.user_id == user_id)

    if not notes:
        await update.message.reply_text("You have no notes yet.")
        return

    response = "📝 Your Notes:\n\n" + "\n\n".join(
        f"{note.id}: {note.title} \n{note.content}" for note in notes
    )
    await update.message.reply_text(response)


# UPDATE: /editnote <id> <new_content>
async def edit_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    if len(args) < 2:
        await update.message.reply_text("Usage: /editnote <note_id> <new_content>")
        return

    note_id, new_content = args[0], " ".join(args[1:])

    try:
        note = Note.get((Note.user_id == user_id) & (Note.id == note_id))
        note.content = new_content
        note.save()
        await update.message.reply_text(f"Updated note {note.title}")
    except Note.DoesNotExist:
        await update.message.reply_text("Note not found or not yours. Oops.")


# DELETE: /deletenote <id>
async def delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("Usage: /deletenote <note_id>")
        return

    note_id = context.args[0]
    try:
        note = Note.get((Note.user_id == user_id) & (Note.id == note_id))
        note.delete_instance()
        await update.message.reply_text(f"Deleted note: {note.title}")
    except Note.DoesNotExist:
        await update.message.reply_text("Note not found or not yours. Oops.")


# Register handlers
def setup_handlers(app):
    # app.add_handler(CommandHandler("newnote", new_note))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("mynotes", my_notes))
    app.add_handler(CommandHandler("editnote", edit_note))
    app.add_handler(CommandHandler("deletenote", delete_note))



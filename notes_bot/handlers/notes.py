from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from models.note import Note
from api.api import get_bible_verse, get_quran_verse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# STATES for Notes
TITLE, CONTENT = range(2)

# STATES for viewing/editing/deleting notes
VIEW_NOTE, EDIT_NOTE, DELETE_NOTE = range(3)

# Notes per page
NOTES_PER_PAGE = 1


# viewing notes functionality
async def view_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"Starting view_notes for user {user_id}")
    notes = list(Note.select().where(Note.user_id == user_id))
    logger.info(f"Found {len(notes)} notes for user")

    if not notes:
        await update.message.reply_text("You have no notes yet.")
        return ConversationHandler.END

#     save state
    context.user_data["notes"] = notes
    context.user_data["current_index"] = 0

#     show first note
    await send_note_page(update, context)
    return VIEW_NOTE

async def send_note_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notes = context.user_data["notes"]
    index = context.user_data["current_index"]
    note = notes[index]
    logger.info(f"Preparing to display note {index + 1}/{len(notes)}")
#     build message text
    text = f"📝 Note {index + 1} of {len(notes)}\n\n"
    text += f"**Title** {note.title}\n"
    text += f"**Content** {note.content}"

# inline buttons
    keyboard = [
        [
            InlineKeyboardButton("⬅️ Prev", callback_data="prev"),
            InlineKeyboardButton("➡️ Next", callback_data="next"),
        ],
        [
            InlineKeyboardButton("✏️ Edit", callback_data="edit"),
            InlineKeyboardButton("🗑️ Delete", callback_data="delete"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

#     if a new message
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    #     else edit the existing message
    else:
        query = update.callback_query
        await query.edit_message_text(text, reply_markup=reply_markup)


async def handle_note_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info(f"Callback received: {query.data}")

    notes = context.user_data["notes"]
    index = context.user_data["current_index"]
    logger.info(f"Current state - notes: {len(notes)}, index: {index}")

    action = query.data

# handle buttons with a note display
    if action == "prev":
        if index > 0:
            context.user_data["current_index"] -= 1
            await send_note_page(update, context)
    elif action == "next":
        if index < len(notes) - 1:
            context.user_data["current_index"] += 1
            await send_note_page(update, context)
    elif action == "edit":
        await query.edit_message_text("Enter the new content for this note:")
        return EDIT_NOTE
    elif action == "delete":
        note = notes[index]
        note.delete_instance()
        del notes[index]
        context.user_data["notes"] = notes
        if not notes:
            await query.edit_message_text("Note deleted. You have no more notes.")
            return ConversationHandler.END
        if index >= len(notes):
            context.user_data["current_index"] = len(notes) - 1

    await send_note_page(update, context)
    return VIEW_NOTE

async def handle_edit_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    new_content = update.message.text
    notes = context.user_data["notes"]
    index = context.user_data["current_index"]
    note = notes[index]

    note.content = new_content
    note.save()

    await update.message.reply_text("✅ Note updated!")
    return VIEW_NOTE

# canceller for viewing notes
async def cancel_view_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Exited note viewer.")
    return ConversationHandler.END

view_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("viewnotes", view_notes)
    ],
    states={
        VIEW_NOTE: [
            CallbackQueryHandler(handle_note_navigation, pattern="^(prev|next|edit|delete)$"),
        ],
        EDIT_NOTE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_note),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_view_mode),
        CommandHandler("done", cancel_view_mode),
    ],
    allow_reentry=True,
)
logger.info("View notes conversation handler initialized")



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
    verse = ""
    if context.user_data["religion"] == "christian":
        verse = await get_bible_verse()
    if context.user_data["religion"] == "muslim":
        verse = await get_quran_verse()
    content = update.message.text

    Note.create(user_id=user_id, title=title, content=content)

    await update.message.reply_text(f"✅ Note created successfully! Here's a verse for you:\n\n{verse}")
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
# async def my_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     notes = Note.select().where(Note.user_id == user_id)
#
#     if not notes:
#         await update.message.reply_text("You have no notes yet.")
#         return
#
#     response = "📝 Your Notes:\n\n" + "\n\n".join(
#         f"{idx}: {note.title}\n{note.content}" for idx, note in enumerate(notes, start=1)
#     )
#     await update.message.reply_text(response)


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
        await update.message.reply_text("Usage: /deletenote <note_title>")
        return

    note_title = context.args[0]
    try:
        note = Note.get((Note.user_id == user_id) & (Note.title == note_title))
        note.delete_instance()
        await update.message.reply_text(f"Deleted note: {note.title}")
    except Note.DoesNotExist:
        await update.message.reply_text("Note not found or not yours. Oops.")



# Register handlers
def setup_handlers(app):
    # app.add_handler(CommandHandler("newnote", new_note))
    app.add_handler(conv_handler)
    app.add_handler(view_conv_handler)
    app.add_handler(CommandHandler("mynotes", my_notes))
    app.add_handler(CommandHandler("editnote", edit_note))
    app.add_handler(CommandHandler("deletenote", delete_note))



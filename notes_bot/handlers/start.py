from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Starts the bot, gives a user choice of religion.
    Based on the choice certain passages will be attached to the notes.
    """
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a BibleNotes bot!")
    if "religion" in context.user_data:
        await update.message.reply_text(f"You chose your religion, it's '{context.user_data['religion'].capitalize()}'. Choose other commands from the menu.")

    else :
        keyboard = [

                [InlineKeyboardButton("Christian", callback_data="religion_christian"),],
                [InlineKeyboardButton("Muslim", callback_data="religion_muslim"),],
                [InlineKeyboardButton("Atheist", callback_data="religion_atheist"),],

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Choose your religion:", reply_markup=reply_markup)


async def handle_religion_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the religion choice.
    Sets up a religion to context.user_data if 'christian' or 'muslim' is chosen.
    If 'atheist' is chosen, shows a 'sorry message' to a user.
    """
    query = update.callback_query
    await query.answer()
    logger.info(f"Callback received: {query.data}")
    # user_id = query.from_user.id
    choice = query.data
    success_message = "You can create notes here: /newnote <title> <content>, edit them: /editnote <note.title> <new_content>, delete them: /deletenote <note.title>, and see the list of all notes: /mynotes."


    if choice == "religion_atheist":
        await query.edit_message_text(text="Sorry, you must be religious.")
    elif choice == "religion_christian":
        context.user_data["religion"] = "christian"
        await query.edit_message_text(text=success_message)
    elif choice == "religion_muslim":
        context.user_data["religion"] = "muslim"
        await query.edit_message_text(text=success_message)


async def hello_world(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, World!")



async def post_init(app):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("helloworld", "Hello world!"),
        BotCommand("newnote", "Create a new note"),
        BotCommand("viewnotes", "View and edit your notes"),
        BotCommand("mynotes", "Show your notes"),
        BotCommand("editnote", "Edit your notes by id"),
        BotCommand("deletenote", "Delete your notes by id"),

    ]
    await app.bot.set_my_commands(commands)


def setup_handlers_onstart(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("helloworld", hello_world))
    app.add_handler(CallbackQueryHandler(handle_religion_choice, pattern="^religion_"))
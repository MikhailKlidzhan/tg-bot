from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)
from loguru import logger


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Starts the bot, gives a user choice of religion.
    Based on the choice certain passages will be attached to the notes.
    """
    if "religion" in context.user_data:
        await update.message.reply_text(
            f"You chose your religion, it's '{context.user_data['religion'].capitalize()}'. Choose other commands from the menu."
        )

    else:
        keyboard = [
            [
                InlineKeyboardButton("Christian", callback_data="religion_christian"),
            ],
            [
                InlineKeyboardButton("Muslim", callback_data="religion_muslim"),
            ],
            [
                InlineKeyboardButton("Atheist", callback_data="religion_atheist"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Choose your religion:", reply_markup=reply_markup
        )


async def handle_religion_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the religion choice.
    Sets up a religion to context.user_data if 'christian' or 'muslim' is chosen.
    If 'atheist' is chosen, shows a 'sorry message' to a user.
    """
    query = update.callback_query
    await query.answer()
    logger.info(f"Callback received: {query.data}")
    choice = query.data
    success_message = (
        "You can create notes here: /newnote.\nView, edit and delete them: /viewnotes."
    )

    if choice == "religion_atheist":
        await query.edit_message_text(text="Sorry, you must be religious.")
    elif choice == "religion_christian":
        context.user_data["religion"] = "christian"
        await query.edit_message_text(text=success_message)
    elif choice == "religion_muslim":
        context.user_data["religion"] = "muslim"
        await query.edit_message_text(text=success_message)


async def post_init(app):
    """Initializes available commands for the bots"""
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("newnote", "Create a new note"),
        BotCommand("viewnotes", "View, edit or delete your notes"),
    ]
    await app.bot.set_my_commands(commands)


def setup_handlers_onstart(app):
    """Adds handlers to the app upon the start command"""
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_religion_choice, pattern="^religion_"))

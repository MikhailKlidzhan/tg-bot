from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a BibleNotes bot!")
    keyboard = [
        InlineKeyboardButton("Christian", callback_data="religion_christian"),
        InlineKeyboardButton("Muslim", callback_data="religion_muslim"),
        InlineKeyboardButton("Atheist", callback_data="religion_atheist"),
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose your religion:", reply_markup=reply_markup)


async def hello_world(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, World!")


async def greet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    if "привет" in user_message.lower():
        await update.message.reply_text("Привет, я религиозный бот заметок!")

    else:
        await update.message.reply_text("Попробуй команды из меню. Try commands from the menu.")


async def post_init(app):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("helloworld", "Hello world!"),
        BotCommand("newnote", "Create a new note"),
        BotCommand("mynotes", "Show your notes"),
        BotCommand("editnote", "Edit your notes by id"),
        BotCommand("deletenote", "Delete your notes by id"),

    ]
    await app.bot.set_my_commands(commands)


def setup_handlers_onstart(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("helloworld", hello_world))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, greet))
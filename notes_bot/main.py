from loguru import logger
from telegram.ext import ApplicationBuilder
from dotenv import load_dotenv
import os
import sys

from handlers.start import setup_handlers_onstart, post_init
from handlers.notes import setup_handlers

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

logger.remove()

logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)

logger.add(
    "logs/bot_info.log",
    rotation="1 day",
    retention="7 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level <8} | {name}:{function}:{line} - {message}",
    level="INFO",
)

logger.add(
    "logs/bot_errors.log",
    rotation="1 day",
    retention="30 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    setup_handlers_onstart(app)
    setup_handlers(app)


    app.run_polling()
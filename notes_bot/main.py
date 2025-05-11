import logging
from telegram.ext import ApplicationBuilder
from dotenv import load_dotenv
import os

from handlers.start import setup_handlers_onstart, post_init
from handlers.notes import setup_handlers

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')



logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    setup_handlers_onstart(app)
    setup_handlers(app)


    app.run_polling()
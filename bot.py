import os
import sys
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from bot.handlers.handlers import start_command, menu_command, go_back, handle_menu_selection, change_language_command, change_language
from bot.handlers.address_handlers import confirm_delete, add_address, confirm_address

# from bot.db.database_manager import DatabaseManager
current_dir = os.path.dirname(os.path.abspath(__file__))

# Append the parent directory of current_dir to sys.path
bot_directory = os.path.join(current_dir, 'bot')
sys.path.append(bot_directory)

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(os.getenv('TG_TOKEN')).build()
    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('menu', menu_command))
    # # Message handlers
    app.add_handler(MessageHandler(filters.Regex('^(✅|❌)$'), confirm_address))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_address))
    app.add_handler(CallbackQueryHandler(handle_menu_selection, pattern="^(add_address|delete_address|list_addresses)$"))
    app.add_handler(CallbackQueryHandler(go_back, pattern="^go_back$"))
    app.add_handler(CallbackQueryHandler(confirm_delete, pattern="^deleteaddress_.*"))
    app.add_handler(CallbackQueryHandler(add_address, pattern="^district_.*"))
    app.add_handler(CallbackQueryHandler(change_language_command, pattern="^change_language$"))
    app.add_handler(CallbackQueryHandler(change_language, pattern="^change_language.*"))


    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)

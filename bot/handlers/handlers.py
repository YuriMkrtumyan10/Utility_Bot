from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackContext

from bot.utils.utils import merge, get_reply_markup
from bot.db.db_util import get_cursor
from bot.handlers.address_handlers import add_address_command, show_addresses_command, delete_address_command
from bot.methods.menu import load_menu
from bot.utils.translations import get_language_loader

cursor = get_cursor()
lang_loader = get_language_loader()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute('INSERT OR IGNORE INTO users (id, firstname, username, language_code) VALUES (?, ?, ?, ?)', (
        update.effective_user.id, 
        update.effective_user.first_name,
        update.effective_user.username,
        update.effective_user.language_code,
    ))
    
    lang_loader = get_language_loader()
    lang_loader.load_language_for_user(update.effective_user.id)

    await update.message.reply_text(lang_loader.get_translation("welcome_message"))

    await menu_command(update, context)

async def menu_command(update: Update, context: CallbackContext) -> None:
    await load_menu(update, context)

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    # await query.answer()
    # await query.message.delete()

    if query.data == "add_address":
        await add_address_command(update, context)
    elif query.data == "delete_address":
        await delete_address_command(update, context)
    elif query.data == "list_addresses":
        await show_addresses_command(update, context)

async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    # await query.message.delete()

    # Remove the "Go Back" message
    # await query.edit_message_text(text="Going back to main menu...")

    # Show the main menu again
    await menu_command(update, context)


async def change_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    lang_loader = get_language_loader()
    lang_loader.load_language_for_user(update.effective_user.id)

    keyboard = [
        [InlineKeyboardButton("🇦🇲 հայերեն 🇦🇲", callback_data="change_language_hy")],
        [InlineKeyboardButton("🇷🇺 Русский 🇷🇺", callback_data="change_language_ru")],
        [InlineKeyboardButton("🇺🇸 English 🇺🇸", callback_data="change_language_en")],
    ]
    reply_markup = get_reply_markup()
    reply_markup = merge(reply_markup, keyboard)

    await update.callback_query.edit_message_text(lang_loader.get_translation("change_language"), reply_markup=reply_markup)

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    language = query.data.split('_')[2]
    cursor.execute("UPDATE users SET language_code = ? WHERE id = ?", (language, user_id))
    cursor.connection.commit()
#    await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    await load_menu(update, context)

import re
from typing import Final
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackContext, CallbackQueryHandler
import langid
from dotenv import load_dotenv
import os
from helpers.constants import districts
from helpers.helpers import get_key_by_value
load_dotenv()


TOKEN: Final = os.getenv('TG_TOKEN')
BOT_USERNAME: Final = '@komunal_anjatumner_bot'
import sqlite3

conn = sqlite3.connect('utility_project.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, firstname TEXT, username TEXT, language_code TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS user_addresses (id INTEGER PRIMARY KEY, address TEXT, address_number INT, user_id INT)')
conn.commit()

# conversation_states
PROVINCE_SELECTION_IN_PROGRESS, ADDING_ADDRESS, ADDING_CONFIRMATION, SELECT_ADDRESS_DELETE, CONFIRM_ADDRESS_DELETE = range(5)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # await update.message.reply_text("privet balyat, eshi axuet chanis stx")
    cursor.execute('INSERT OR IGNORE INTO users (id, firstname, username, language_code) VALUES (?, ?, ?, ?)', (
        update.effective_user.id, 
        update.effective_user.first_name,
        update.effective_user.username,
        update.effective_user.language_code,
    ))

    conn.commit()
    await select_province(update, context)

async def add_address_command(update: Update, context: CallbackContext) -> None:
    await select_province(update, context)

async def select_province(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Please select your province name:")
    
    # Create a custom keyboard with Yerevan provinces
    custom_keyboard = [[KeyboardButton(province)] for i, province in districts.items()]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, selective=True)
    
    await update.message.reply_text("Ընտրեք Ձեր մարզը։", reply_markup=reply_markup)

    # Set a flag in user data to indicate that province selection is in progress
    context.user_data["conversation_state"] = PROVINCE_SELECTION_IN_PROGRESS

async def add_address(update: Update, context: CallbackContext) -> None:
    if context.user_data.get("conversation_state") == PROVINCE_SELECTION_IN_PROGRESS:
        context.user_data["selected_province"] = update.message.text
        await update.message.reply_text("Please enter your address:", reply_markup=ReplyKeyboardRemove())
        context.user_data["conversation_state"] = ADDING_ADDRESS
    elif context.user_data.get("conversation_state") == ADDING_ADDRESS:
        context.user_data["conversation_state"] = -1
        user_address = update.message.text
        lang, _ = langid.classify(user_address)
        if lang != 'hy':  # 'hy' is the ISO 639-1 code for Armenian
            await update.message.reply_text("Please enter your message in Armenian.")
            return
        
        context.user_data["address"] = user_address
        custom_keyboard = [["Այո", "Ոչ"]]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, selective=True)
        context.user_data["conversation_state"] = ADDING_CONFIRMATION
        await update.message.reply_text(f"Դուք գրել եք `{user_address}`։ Հաստատեք ձեր հասցեն` Այո` կամ `Ոչ`։",
                                        reply_markup=reply_markup)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

async def confirm_address(update: Update, context: CallbackContext) -> None:
    if context.user_data.get("conversation_state") == ADDING_CONFIRMATION:
        context.user_data["conversation_state"] = -1
        button_click = update.message.text
        if button_click == "Այո":
            user_id = update.effective_user.id
            province = context.user_data.get("selected_province")
            address = context.user_data.get("address")
            match = re.match(r"([^0-9]+)\s(.+)$", address)
            if match:
                street_name = match.group(1).strip()
                address_number = match.group(2).strip()

                # Handle special case for "փ." in street_name
                if "փ." in street_name:
                    street_name = street_name.replace("փ.", "").strip()
                    address_number = "փ. " + address_number
                print('province', get_key_by_value(districts, province))
                cursor.execute('INSERT INTO user_addresses (address, address_number, user_id, province) VALUES (?, ?, ?, ?)', (
                    street_name,
                    address_number,
                    user_id,
                    get_key_by_value(districts, province)
                ))
                conn.commit()

                await update.message.reply_text(f"Ձեր հասցեն `{address}` հաջողությամբ ավելացվել է։ Շնորհակալություն։", reply_markup=ReplyKeyboardRemove())
            else:
                street_name = address.strip()
                address_number = ""
                await update.message.reply_text("Ֆորմատյ սխալա", reply_markup=ReplyKeyboardRemove())
        else:
            await update.message.reply_text("Կներեք խնդրի համար։ Կրկին փորձեք։", reply_markup=ReplyKeyboardRemove())

async def delete_address_command(update: Update, context: CallbackContext) -> None:

    user_id = update.effective_user.id
    cursor.execute('SELECT id, address, address_number FROM user_addresses WHERE user_id = ?', (user_id,))
    addresses = cursor.fetchall()

    if not addresses:
        await update.message.reply_text("There are no existing addresses to delete.")
        return

    # Create a custom keyboard with buttons for each address
    # address_buttons = [[KeyboardButton(f"{address[0]} {address[1]}")] for address in addresses]
    context.user_data["conversation_state"] = SELECT_ADDRESS_DELETE
    keyboard = [[InlineKeyboardButton(f"{address[1]} {address[2]}", callback_data=str(address[0]))] for address in addresses]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Select the address you want to delete:", reply_markup=reply_markup)
    
async def confirm_delete(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    selected_address_index = int(query.data)
    # addresses = context.user_data.get("addresses")
    print(selected_address_index)
    user_id = query.from_user.id

    cursor.execute('DELETE FROM user_addresses WHERE id = ? AND user_id = ?', (selected_address_index, user_id))
    conn.commit()

    await query.message.reply_text(f"The address has been successfully deleted.")
    context.user_data["conversation_state"] = -1

    # elif context.user_data.get("conversation_state") == CONFIRM_ADDRESS_DELETE:
    #     selected_address = update.message.text
    #     user_id = update.effective_user.id

    #     cursor.execute('DELETE FROM user_addresses WHERE address = ? AND user_id = ?', (selected_address, user_id))
    #     conn.commit()

    #     await update.message.reply_text(f"The address '{selected_address}' has been successfully deleted.")
    #     context.user_data["conversation_state"] = -1

    # else:
    #     pass

async def show_addresses_command(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    cursor.execute('SELECT address, address_number, province FROM user_addresses WHERE user_id = ?', (user_id,))
    addresses = cursor.fetchall()
   
    if not addresses:
        await update.message.reply_text("There are no existing addresses.")
        return

    formatted_addresses = "\n".join(f"{address[0]} {address[1]}" for address in addresses)

    await update.message.reply_text("Existing Addresses:\n" + formatted_addresses)

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    
    # Add handler for confirmation message
    app.add_handler(MessageHandler(filters.Regex('^(Այո|Ոչ)$'), confirm_address))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_address))
    app.add_handler(CallbackQueryHandler(confirm_delete))
    app.add_handler(CommandHandler('new_address', add_address_command))
    app.add_handler(CommandHandler('remove_address', delete_address_command))
    app.add_handler(CommandHandler('list_addresses', show_addresses_command))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackContext, CallbackQueryHandler

from bot.utils.translations import get_language_loader, get_user_language_code
from bot.db.db_util import get_cursor
from bot.utils.utils import merge, get_reply_markup
from bot.utils.translate import detect_language, translate_address_to_armenian
from bot.methods.address_methods import select_province
from bot.utils.utils import get_districts
import re
from helpers.helpers import get_key_by_value
from bot.constants import *
from bot.methods.menu import load_menu
cursor = get_cursor()

lang_loader = get_language_loader()


async def add_address_command(update: Update, context: CallbackContext) -> None:
    await select_province(update, context)

async def show_addresses_command(update: Update, context: CallbackContext) -> None:

    lang_loader.load_language_for_user(update.effective_user.id)    
    
    reply_markup = get_reply_markup()
    user_id = update.effective_user.id
    cursor.execute('SELECT address, address_number, province FROM user_addresses WHERE user_id = ?', (user_id,))
    addresses = cursor.fetchall()
    
    if not addresses:
        await update.callback_query.edit_message_text(lang_loader.get_translation("no_address_error_message"), reply_markup=reply_markup)
        return

    formatted_addresses = "\n".join(f"📍 {address[0]} {address[1]}" for address in addresses)

    await update.callback_query.edit_message_text(lang_loader.get_translation("list_addresses_command")+ "\n\n" + formatted_addresses, reply_markup=reply_markup)

async def delete_address_command(update: Update, context: CallbackContext) -> None:

    lang_loader.load_language_for_user(update.effective_user.id)
    
    reply_markup = get_reply_markup()
    user_id = update.effective_user.id
    cursor.execute('SELECT id, address, address_number FROM user_addresses WHERE user_id = ?', (user_id,))
    addresses = cursor.fetchall()

    if not addresses:
        await update.callback_query.edit_message_text(lang_loader.get_translation("no_address_error_message"),  reply_markup=reply_markup)
        return

    context.user_data["conversation_state"] = SELECT_ADDRESS_DELETE
    keyboard = [[InlineKeyboardButton(f"📍 {address[1]} {address[2]}", callback_data=f"deleteaddress_{str(address[0])}")] for address in addresses]
    reply_markup = merge(reply_markup, keyboard)
    await update.callback_query.edit_message_text(lang_loader.get_translation("choose_address_to_delete"),  reply_markup=reply_markup)

async def confirm_delete(update: Update, context: CallbackContext) -> None:
    lang_loader.load_language_for_user(update.effective_user.id)
    
    query = update.callback_query
    await query.answer()

    selected_address_index = int(query.data.split('_')[1])
    # addresses = context.user_data.get("addresses")
    user_id = query.from_user.id

    cursor.execute('DELETE FROM user_addresses WHERE id = ? AND user_id = ?', (selected_address_index, user_id))
    cursor.connection.commit()
    
    await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    await query.message.reply_text(lang_loader.get_translation("address_successfully_deleted"))
    await load_menu(update, context, 1)
    context.user_data["conversation_state"] = -1

async def add_address(update: Update, context: CallbackContext) -> None:
    lang_loader.load_language_for_user(update.effective_user.id)
    user_id = update.effective_user.id

    if context.user_data.get("conversation_state") == PROVINCE_SELECTION_IN_PROGRESS:
        query = update.callback_query
        district = int(query.data.split('_')[1])
        context.user_data["selected_province"] = get_districts(get_user_language_code(user_id))[district]
        await update.callback_query.edit_message_text(lang_loader.get_translation("add_your_address_message"), reply_markup=get_reply_markup())
        context.user_data["conversation_state"] = ADDING_ADDRESS
    elif context.user_data.get("conversation_state") == ADDING_ADDRESS:
        user_address = update.message.text
        lang = detect_language(user_address)


        if lang != get_user_language_code(update.effective_user.id):  # 'hy' is the ISO 639-1 code for Armenian
            await update.message.reply_text(lang_loader.get_translation("address_in_armenian_error_message"))
            return
        pattern = r"^\D+\s+\d+(?:/\d+)?$"

        match = re.match(pattern, user_address)
        if not(match):
            await update.message.reply_text(lang_loader.get_translation("wrong_address_format"), reply_markup=ReplyKeyboardRemove())
            return
        context.user_data["conversation_state"] = -1

        context.user_data["address"] = user_address
        custom_keyboard = [["✅", "❌"]]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, selective=True)
        context.user_data["conversation_state"] = ADDING_CONFIRMATION
        await update.message.reply_text(
                lang_loader.get_translation("recheck_address_part1") + 
                f""" "{user_address}"🏠\n\n""" +
                lang_loader.get_translation("recheck_address_part2"), 
            parse_mode='HTML', reply_markup=reply_markup)
        # await update.message.reply_text(, parse_mode='HTML', reply_markup=reply_markup)

async def confirm_address(update: Update, context: CallbackContext) -> None:

    lang_loader.load_language_for_user(update.effective_user.id)
    
    if context.user_data.get("conversation_state") == ADDING_CONFIRMATION:
        context.user_data["conversation_state"] = -1
        button_click = update.message.text
        if button_click == "✅":
            user_id = update.effective_user.id
            province = context.user_data.get("selected_province")
            address = context.user_data.get("address")
            match = re.match(r"([^0-9]+)\s(.+)$", address)
            if match:
                street_name = match.group(1).strip()
                address_number = match.group(2).strip()

                if "փ." in street_name:
                    street_name = street_name.replace("փ.", "").strip()
                    address_number = "փ. " + address_number

                cursor.execute('INSERT INTO user_addresses (address, address_hy, address_number, user_id, province) VALUES (?, ?, ?, ?, ?)', (
                    street_name,
                    translate_address_to_armenian(street_name, get_user_language_code(update.effective_user.id)),
                    address_number,
                    user_id,
                    get_key_by_value(get_districts(get_user_language_code(user_id)), province)
                ))
                cursor.connection.commit()

                await update.message.reply_text(lang_loader.get_translation("address_successfully_added_part1") + f""" "{address}" """ + lang_loader.get_translation("address_successfully_added_part2"), reply_markup=ReplyKeyboardRemove())
                
                await load_menu(update, context)
        else:
            await update.message.reply_text(lang_loader.get_translation("try_again_message"), reply_markup=ReplyKeyboardRemove())
            await load_menu(update, context)


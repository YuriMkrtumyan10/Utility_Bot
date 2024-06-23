from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton
from ..utils.translations import get_language_loader

async def load_menu(update, context, newMessage = -1):

    lang_loader = get_language_loader()
    lang_loader.load_language_for_user(update.effective_user.id)


    keyboard = [
        [InlineKeyboardButton(lang_loader.get_translation("add_address_command"), callback_data="add_address")],
        [InlineKeyboardButton(lang_loader.get_translation("delete_address_command"), callback_data="delete_address")],
        [InlineKeyboardButton(lang_loader.get_translation("list_addresses_command"), callback_data="list_addresses")],
        [InlineKeyboardButton(lang_loader.get_translation("change_language_command"), callback_data="change_language")],
        [InlineKeyboardButton(lang_loader.get_translation("support_command"), url="https://t.me/komunal_anjatumnet_support")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(lang_loader.get_translation("select_below"), reply_markup=reply_markup)
    elif update.callback_query:
        if newMessage == 1:
            await update.callback_query.message.reply_text(lang_loader.get_translation("select_below"), reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text(lang_loader.get_translation("select_below"), reply_markup=reply_markup)
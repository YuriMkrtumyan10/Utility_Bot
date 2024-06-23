import re
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from bot.utils.translations import get_language_loader, get_user_language_code
from bot.constants import *
from bot.db.db_util import get_cursor
from helpers.helpers import get_key_by_value
from bot.utils.utils import merge, get_reply_markup, get_districts

cursor = get_cursor()

async def select_province(update: Update, context: CallbackContext) -> None:
    lang_loader = get_language_loader()
    lang_loader.load_language_for_user(update.effective_user.id)
    user_id = update.effective_user.id

    reply_markup = get_reply_markup()
    await update.callback_query.answer()
    # await update.callback_query.edit_message_text("Please select your province name:", reply_markup=reply_markup)
    districts = get_districts(get_user_language_code(user_id))
    # Assuming districts is a dictionary where keys are integers and values are province names
    custom_keyboard = [[InlineKeyboardButton(province, callback_data=f"district_{str(key)}")] for key, province in districts.items()]
    reply_markup = merge(reply_markup, custom_keyboard)


    await update.callback_query.edit_message_text(lang_loader.get_translation("select_province_message"),reply_markup=reply_markup)

    context.user_data["conversation_state"] = PROVINCE_SELECTION_IN_PROGRESS


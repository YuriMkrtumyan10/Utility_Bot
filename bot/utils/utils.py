from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from .translations import get_language_loader
from helpers.constants import districts
def merge(reply_markup, keyboard):
    existing_buttons = reply_markup.inline_keyboard if reply_markup else []

    if isinstance(keyboard, list):
        keyboard = tuple(keyboard)

    combined_keyboard = keyboard + existing_buttons

    return InlineKeyboardMarkup(combined_keyboard)

def get_reply_markup():
    
    lang_loader = get_language_loader()
    # lang_loader.load_language_for_user(update.effective_user.id)
    
    keyboard = [[InlineKeyboardButton(lang_loader.get_translation("go_back"), callback_data="go_back")]]
    return InlineKeyboardMarkup(keyboard)

def get_districts(lang):
    result = {}
    for key, value in districts.items():
        result[key] = value[lang]
    return result
import os
import json
from bot.db.db_util import get_cursor

cursor = get_cursor()

class LanguageLoader:
    def __init__(self, lang_folder='lang', default_lang='en'):
        self.lang_folder = lang_folder
        self.default_lang = default_lang
        self.translations = {}
        self.load_default_language()

    def load_default_language(self):
        self.load_language(self.default_lang)

    def load_language(self, lang_code):
        lang_file = os.path.join(self.lang_folder, f'{lang_code}.json')
        if not os.path.exists(lang_file):
            raise FileNotFoundError(f"Language file '{lang_code}.json' not found in '{self.lang_folder}'")

        with open(lang_file, 'r', encoding='utf-8') as file:
            self.translations = json.load(file)

    def load_language_for_user(self, user_id):
        lang_code = get_user_language_code(user_id)
        self.load_language(lang_code)

    def get_translation(self, key):
        return self.translations.get(key, f"Translation for '{key}' not found")

_language_loader = None

def get_language_loader():
    global _language_loader
    if _language_loader is None:
        detected_language = detect_language()
        _language_loader = LanguageLoader(default_lang=detected_language)
    return _language_loader

def detect_language():
    return os.getenv('APP_LANGUAGE', 'en')


def get_user_language_code(user_id):
    cursor.execute("SELECT language_code FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    return 'en'
# from deep_translator import GoogleTranslator

# def translate_address_to_armenian(text, source):
#     translator = GoogleTranslator(source=source, target='hy')
#     translation = translator.translate(text)
#     return translation

# Example usage:
text_ru = "Алабян 12"
text_en = "Ruben Sevak 24"
text_hy = "бангладе 41"

print(detect_language(text_ru))  # Output: 'ru'
print(detect_language(text_en))  # Output: 'en'
print(detect_language(text_hy))  # Output: 'hy'

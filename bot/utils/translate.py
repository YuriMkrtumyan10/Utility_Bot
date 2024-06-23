from deep_translator import GoogleTranslator

def translate_address_to_armenian(text, source):
    translator = GoogleTranslator(source=source, target='hy')
    translation = translator.translate(text)
    return translation

def translate_from_armenian(text, lang):
    translator = GoogleTranslator(source='hy', target=lang)
    translation = translator.translate(text)
    return translation

def detect_language(text):
    if any(char in text for char in 'ԱԲԳԴԵԶԷԸԹԺԻԼԽԾԿՀՁՂՃՄՅՆՇՈՉՊՋՌՍՎՏՐՑՒՓՔՕՖաբգդեզէըթժիլխծկհձղճմյնշոչպջռսվտրցւփքօֆ'):
        return 'hy'  # Armenian
    elif any(char in text for char in 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя'):
        return 'ru'  # Russian
    elif any(char in text for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'):
        return 'en'  # English
    else:
        return 'unknown'
    
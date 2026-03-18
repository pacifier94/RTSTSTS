import argostranslate.translate

langs = argostranslate.translate.get_installed_languages()

for lang in langs:
    print("Language:", lang.code)
    for t in lang.translations_to:
        print("   ->", t.to_lang.code)

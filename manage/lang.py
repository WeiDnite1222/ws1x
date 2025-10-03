import json
import os


class LanguageUtil:
    def __init__(self, languages_dir, current_language):
        self.languages_dir = languages_dir
        self.current_language = current_language
        self.__CURRENT_LANG_FILE_NOTFOUND = False
        self.LANG_DICTIONARY = {}

        self.load_language()

    def load_language(self):
        current_language_filepath = os.path.join(self.languages_dir, f'{self.current_language}.json')

        if not os.path.exists(current_language_filepath):
            self.__CURRENT_LANG_FILE_NOTFOUND = True
            print(f'ERROR: Current language pack not found at {current_language_filepath}')
            return

        try:
            with open(current_language_filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

                self.LANG_DICTIONARY = data
        except Exception as e:
            print(f'ERROR: Reading current language pack failed: {e}')
            return
        
    def __call__(self, text, *kwargs):
        localization_text = self.LANG_DICTIONARY.get(text, text)

        format_str_bracket = localization_text.count("{}")

        if format_str_bracket > 0:
            for count in range(format_str_bracket):
                try:
                    replace_format_string = self.LANG_DICTIONARY.get(kwargs[count], f"${kwargs[count]}")
                except KeyError:
                    continue
                localization_text = localization_text.replace("{}", replace_format_string, count+1)

        return localization_text
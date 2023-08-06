class LanguageToLanguageTag:
    default_language: str = 'Polish'
    languages: dict = {
        'English': 'en-GB',
        'German': 'de-DE',
        'Polish': 'pl-PL',
    }
    selected_language: str = ''
    selected_tag: str = ''

    def __init__(self, language_name: str) -> None:
        self.selected_language = language_name if language_name in self.__class__.languages.keys() \
            else self.default_language

    def __str__(self) -> str:
        self.selected_tag = str(self.__class__.languages[self.selected_language])
        return self.selected_tag

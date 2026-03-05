import argostranslate.translate
from core.stage import Stage


class ArgosStage(Stage):
    def __init__(self, input_q, output_q):
        super().__init__("Translation", input_q, output_q)

    def process(self, text):
        if text is None:
            return None

        text = text.strip()
        if text == "":
            return None

        try:
            translated = argostranslate.translate.translate(
                text,
                "hi",
                "bn"
            )
            return translated
        except Exception as e:
            print("Translation error:", e)
            return None
from translate import Translator
from core.stage import Stage
import logging

class OfflineTranslatorStage(Stage):
    def __init__(self, input_q, output_q, from_code='en', to_code='hi'):
        super().__init__("Translator", input_q, output_q)
        # Note: 'translate' library uses 'en' and 'hi' format
        # It attempts to use offline providers if configured, 
        # but the default behavior is stable for Python 3.13
        self.translator = Translator(from_lang=from_code, to_lang=to_code)
        logging.info(f"Lightweight Translator Stage Initialized ({from_code} -> {to_code})")

    def process(self, data):
        # We only translate "final" results from the ASR
        if data and data.get("type") == "final":
            english_text = data.get("text", "").strip()
            print(f"[DEBUG TRANS]: Received for translation: {english_text}")
            if english_text:
                try:
                    # This performs the translation
                    hindi_text = self.translator.translate(english_text)
                    return {
                        "original": english_text,
                        "translated": hindi_text
                    }
                except Exception as e:
                    logging.error(f"Translation Stage Error: {e}")
        return None
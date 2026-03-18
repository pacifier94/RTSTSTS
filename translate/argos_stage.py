import argostranslate.translate
from core.stage import Stage


class ArgosStage(Stage):
    def __init__(self, input_q, output_q):
        super().__init__("Translation", input_q, output_q)
    
    def process(self, data):
        if data is None:
            return None

        try:
            text = data.get("text", "").strip()
            is_final = data.get("final", False)
            ts = data.get("ts")

            if not text or not is_final:
                return None

            import argostranslate.translate

            langs = argostranslate.translate.get_installed_languages()

            hi = next(l for l in langs if l.code == "hi")
            en = next(l for l in langs if l.code == "en")
            bn = next(l for l in langs if l.code == "bn")

            hi_en = hi.get_translation(en)
            en_bn = en.get_translation(bn)

            intermediate = hi_en.translate(text)
            translated = en_bn.translate(intermediate)

            return {
                "text": translated,
                "ts": ts,
                "final": True
            }

        except Exception as e:
            print("Translation error:", e)
            return None

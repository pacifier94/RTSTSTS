# --- FORCE DISABLE STANZA COMPLETELY (OFFLINE SAFE) ---
import sys
import types

fake_stanza = types.ModuleType("stanza")


class DummyPipeline:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, text):
        class Doc:
            def __init__(self, text):
                self.sentences = [type("Sent", (), {"text": text})()]

        return Doc(text)


fake_stanza.Pipeline = DummyPipeline
sys.modules["stanza"] = fake_stanza


# --- ARGOS IMPORTS (AFTER PATCH) ---
import argostranslate.package

argostranslate.package.update_package_index = lambda: None

import argostranslate.translate


# --- PIPELINE STAGE ---
from core.stage import Stage


class ArgosStage(Stage):
    def __init__(self, input_q, output_q, ui_callback=None):
        super().__init__("Translation", input_q, output_q)

        self.ui_callback = ui_callback
        self.hi_en = None
        self.en_bn = None

        try:
            langs = argostranslate.translate.get_installed_languages()
            print("Available:", [l.code for l in langs])

            hi = next(l for l in langs if l.code == "hi")
            en = next(l for l in langs if l.code == "en")
            bn = next(l for l in langs if l.code == "bn")

            print("Loading HI → EN...")
            self.hi_en = hi.get_translation(en)

            print("Loading EN → BN...")
            self.en_bn = en.get_translation(bn)

            print("Translation models loaded successfully!")

        except Exception as e:
            print(f"ArgosStage Init Error: {e}")

    def process(self, data):
        if not data or not self.hi_en:
            return None

        # safety check
        if not isinstance(data, dict):
            print("Invalid input to translation:", data)
            return None

        text = data.get("text", "").strip()
        ts = data.get("ts")

        if not text:
            return None

        try:
            # HI → EN → BN
            inter = self.hi_en.translate(text)
            final_text = self.en_bn.translate(inter)

            # UI update
            if self.ui_callback:
                self.ui_callback(text, final_text)

            return {
                "text": final_text,
                "ts": ts,
                "final": True,
            }

        except Exception as e:
            print(f"Translation error: {e}")
            return None

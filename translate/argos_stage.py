import sys
import types
import os
import argostranslate.translate
import argostranslate.settings
from core.stage import Stage
fake_stanza = types.ModuleType("stanza")
argostranslate.settings.enable_sbd = False

class DummySentence:
    def __init__(self, text):
        self.text = text

class DummyDoc:
    def __init__(self, text):
        self.sentences = [DummySentence(text)]

def dummy_pipeline(*args, **kwargs):
    class Dummy:
        def __call__(self, text):
            return DummyDoc(text)
    return Dummy()

fake_stanza.Pipeline = dummy_pipeline

sys.modules['stanza'] = fake_stanza


class ArgosStage(Stage):
    # Add ui_callback=None here to match the call in main.py
    def __init__(self, input_q, output_q, ui_callback=None):
        super().__init__("Translation", input_q, output_q)
        self.ui_callback = ui_callback # Store it if you want to use it later
        self.hi_en = None
        self.en_bn = None
        
        try:
            # 2. Get languages already on disk
            langs = argostranslate.translate.get_installed_languages()
            
            # Find the nodes
            hi = next(l for l in langs if l.code == "hi")
            en = next(l for l in langs if l.code == "en")
            bn = next(l for l in langs if l.code == "bn")

            # 3. Pre-load the translation links
            # This is the line that triggers Stanza. 
            self.hi_en = hi.get_translation(en)
            self.en_bn = en.get_translation(bn)
            
        except Exception as e:
            print(f"ArgosStage Init Error: {e}")

    def process(self, data):
       
        if data is None or self.hi_en is None:
            return None

        try:
            text = data.get("text", "").strip()
            is_final = data.get("final", False)
            ts = data.get("ts")

            if not text or not is_final:
                return None

            # Translate through the English pivot
            inter = self.hi_en.translate(text)
            final_text = self.en_bn.translate(inter)
            if self.ui_callback:
                self.ui_callback(text, final_text, ts=ts)
            
            return {
                "text": final_text,
                "ts": ts,
                "final": True
            }
        except Exception as e:
            print(f"Translation Loop Error: {e}")
            return None

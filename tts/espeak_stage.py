import subprocess
import shutil
from core.stage import Stage
from indic_transliteration import sanscript
from shared_state import is_speaking
class EspeakStage(Stage):
    def __init__(self, input_q):
        super().__init__("TTS", input_q, None)
        # Check path for espeak-ng
        self.executable = shutil.which("espeak-ng")

    def process(self, data):
        if not data:
            return None

        text = data.get("text", "")

        try:
            is_speaking.set()   #START SPEAKING

            subprocess.run(
                ["espeak", text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        finally:
            is_speaking.clear()  #DONE SPEAKING

        return None

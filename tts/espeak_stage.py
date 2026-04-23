import subprocess
import threading
from core.stage import Stage
from shared_state import is_speaking

class EspeakStage(Stage):
    def __init__(self, input_q):
        super().__init__("TTS", input_q, None)

    def speak_async(self, text):
        def run():
            try:
                is_speaking.set()

                subprocess.run(
                    ["espeak-ng", text],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            finally:
                is_speaking.clear()

        threading.Thread(target=run, daemon=True).start()

    def process(self, data):
        if not data:
            return None

        text = data.get("text", "")
        if text:
            self.speak_async(text)

        return None

import subprocess
from core.stage import Stage


class EspeakStage(Stage):
    def __init__(self, input_q):
        super().__init__("TTS", input_q, None)

    def process(self, text):
        if text is None:
            return None

        text = text.strip()
        if text == "":
            return None

        try:
            subprocess.run(
                ["espeak-ng", "-v", "bn", text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            print("TTS error:", e)

        return None
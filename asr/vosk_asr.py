import json
import time
import numpy as np

from vosk import Model, KaldiRecognizer
from core.stage import Stage


class VoskASR(Stage):
    def __init__(self, input_q, output_q, model_path):
        super().__init__("ASR", input_q, output_q)

        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.recognizer.SetWords(True)

        # prevent duplicates
        self.last_text = ""

    def process(self, audio_chunk):
        if audio_chunk is None:
            return None

        if isinstance(audio_chunk, np.ndarray):
            audio_bytes = audio_chunk.tobytes()
        else:
            audio_bytes = audio_chunk

        if self.recognizer.AcceptWaveform(audio_bytes):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").strip()

            if not text:
                return None

            # ignore noise
            if len(text.split()) < 2:
                return None

            return {
                "text": text,
                "final": True,
                "ts": time.time(),
            }

        return None

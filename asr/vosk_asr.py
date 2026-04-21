import json
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

        # convert to bytes
        if isinstance(audio_chunk, np.ndarray):
            audio_bytes = audio_chunk.tobytes()
        else:
            audio_bytes = audio_chunk

        if self.recognizer.AcceptWaveform(audio_bytes):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").strip()

            # empty
            if not text:
                return None

            words = text.split()

            # too short (noise)
            if len(words) < 2:
                return None

            # too long (garbage hallucination)
            if len(words) > 15:
                return None

            # duplicate
            if text == self.last_text:
                return None

            self.last_text = text

            return {
                "text": text,
                "final": True
            }

        return None

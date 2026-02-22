from core.stage import Stage
import time

class DummyASR(Stage):
    def process(self, audio_chunk):
        if audio_chunk:
            time.sleep(0.2)  # simulate inference
            return "recognized speech chunk"

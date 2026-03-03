from core.stage import Stage
import numpy as np
import time


class DummyASR(Stage):
    def process(self, audio_chunk):
        # Proper check for numpy array
        if audio_chunk is None:
            return None

        if isinstance(audio_chunk, np.ndarray) and audio_chunk.size > 0:
            time.sleep(0.2)  # simulate processing
            return "recognized speech chunk"

        return None

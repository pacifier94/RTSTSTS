import sounddevice as sd
import numpy as np
import queue
from core.stage import Stage

class MicStage(Stage):
    def __init__(self, output_q, samplerate=16000, blocksize=8000):
        super().__init__("Mic", None, output_q)
        self.samplerate = samplerate
        self.blocksize = blocksize

    def process(self, _):
        data = sd.rec(self.blocksize,
                      samplerate=self.samplerate,
                      channels=1,
                      dtype="int16")
        sd.wait()
        return data.tobytes()

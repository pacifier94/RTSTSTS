import numpy as np
import sounddevice as sd
from core.stage import Stage


class MicStage(Stage):
    def __init__(self, output_q, samplerate=16000, blocksize=1024):
        super().__init__("MicStage", None, output_q)
        self.samplerate = samplerate
        self.blocksize = blocksize

    def run(self):
        def callback(indata, frames, time, status):
            if status:
                print(status)

            # Convert safely to numpy array
            audio_chunk = np.array(indata, copy=True)

            self.output_q.put(audio_chunk)

        with sd.InputStream(
            samplerate=self.samplerate,
            channels=1,
            blocksize=self.blocksize,
            dtype="int16",
            callback=callback,
        ):
            print("MicStage: Listening...")
            while not self._stop_event.is_set():
                sd.sleep(100)

    def process(self, data):
        return data

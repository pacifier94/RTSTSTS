import numpy as np
import sounddevice as sd
from shared_state import is_speaking
from core.stage import Stage


class MicStage(Stage):
    def __init__(self, output_q, samplerate=16000, blocksize=2048, ui_callback=None):
        super().__init__("MicStage", None, output_q)
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.ui_callback = ui_callback

    def run(self):
        def callback(indata, frames, time, status):
            if status:
                print(status)
            if is_speaking.is_set():
             return
            audio_chunk = np.array(indata, copy=True)

            # normalize
            audio_float = audio_chunk.astype(np.float32) / 32768.0
            amplitude = float(np.sqrt(np.mean(audio_float**2)))

            # minimal noise filter
            if amplitude < 0.02:
                return

            try:
                self.output_q.put_nowait(audio_chunk)
            except:
                pass

            if self.ui_callback:
                self.ui_callback(amplitude)

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

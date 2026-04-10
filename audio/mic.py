import numpy as np
import sounddevice as sd
from core.stage import Stage


class MicStage(Stage):
    def __init__(self, output_q, samplerate=16000, blocksize=1024, ui_callback=None):
        super().__init__("MicStage", None, output_q)
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.ui_callback = ui_callback  # NEW

    def run(self):
        def callback(indata, frames, time, status):
            if status:
                print(status)

            # Convert safely to numpy array
            audio_chunk = np.array(indata, copy=True)

           # compute amplitude
            audio_float = audio_chunk.astype(np.float32) / 32768.0
            amplitude = float(np.sqrt(np.mean(audio_float**2)))

            # only send if above threshold
            if amplitude > self.threshold:
                self.output_q.put(audio_chunk)
            #send amplitude to UI
            if self.ui_callback:
                # normalize int16 → float
                audio_float = audio_chunk.astype(np.float32) / 32768.0

                # RMS amplitude
                amplitude = float(np.sqrt(np.mean(audio_float**2)))

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

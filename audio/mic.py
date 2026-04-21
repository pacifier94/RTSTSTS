import numpy as np
import sounddevice as sd
from core.stage import Stage


class MicStage(Stage):
    def __init__(self, output_q, samplerate=16000, blocksize=2048, ui_callback=None, threshold_ref=None):
        super().__init__("MicStage", None, output_q)
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.ui_callback = ui_callback
        self.threshold_ref = threshold_ref  # 🔥 shared with UI

        # Adaptive noise baseline
        self.noise_samples = []
        self.noise_baseline = 0.0

        self.silence_counter = 0
        self.silence_limit = 10
        self.speaking = False

    def run(self):
        def callback(indata, frames, time, status):
            if status:
                print(status)

            audio_chunk = np.array(indata, copy=True)
            audio_float = audio_chunk.astype(np.float32) / 32768.0

            amplitude = float(np.sqrt(np.mean(audio_float**2)))

            # ---------------- ADAPTIVE NOISE LEARNING ----------------
            # continuously update baseline (slow adaptation)
            self.noise_baseline = 0.95 * self.noise_baseline + 0.05 * amplitude

           
            threshold = max(0.02, self.noise_baseline * 2.5)

            # ---------------- UI UPDATE ----------------
            if self.ui_callback:
                self.ui_callback(amplitude)

            # ---------------- SPEECH DETECTION ----------------
            if amplitude > threshold:
                self.speaking = True
                self.silence_counter = 0
                self.output_q.put(audio_chunk)

            else:
                if self.speaking:
                    self.silence_counter += 1
                    if self.silence_counter < self.silence_limit:
                        self.output_q.put(audio_chunk)
                    else:
                        self.speaking = False
                        self.silence_counter = 0

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

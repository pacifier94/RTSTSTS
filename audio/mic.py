import sounddevice as sd
import logging
from core.stage import Stage

class MicStage(Stage):
    def __init__(self, output_q, samplerate=16000, blocksize=4000):
        super().__init__("Mic", None, output_q)
        self.samplerate = samplerate
        self.blocksize = blocksize

    def run(self):
        def callback(indata, frames, time, status):
            if status:
                logging.warning(f"Mic Status: {status}")
            if not self.output_q.full():
                self.output_q.put(indata.copy())
            else:
                logging.warning("MicStage: Output queue is full, dropping audio data.")
        
        try:
            with sd.RawInputStream(samplerate=self.samplerate, 
                                   blocksize=self.blocksize, 
                                   dtype='int16', 
                                   channels=1, 
                                   callback=callback) as stream:
                logging.info("MicStage: Listening...")
                while not self._stop_event.is_set():
                    sd.sleep(100)
        except Exception as e:
            logging.error(f"Error in MicStage: {e}")

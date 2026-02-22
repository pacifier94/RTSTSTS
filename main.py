import queue
import time

from core.pipeline import Pipeline
from audio.mic import MicStage
from asr.dummy_asr import DummyASR


audio_q = queue.Queue()
text_q = queue.Queue()

mic = MicStage(audio_q)
asr = DummyASR("ASR", audio_q, text_q)

pipeline = Pipeline([mic, asr])

pipeline.start()

print("Running pipeline... Ctrl+C to stop")

try:
    while True:
        if not text_q.empty():
            print("TEXT:", text_q.get())
        time.sleep(0.1)

except KeyboardInterrupt:
    pipeline.stop()
    print("Stopped")

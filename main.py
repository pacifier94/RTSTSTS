import queue
import time
import logging

from core.pipeline import Pipeline
from audio.mic import MicStage
from asr.dummy_asr import DummyASR
from translate.argos_stage import ArgosStage
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create the audio and text queues
audio_q = queue.Queue()
text_q = queue.Queue()

# Set up the stages
mic = MicStage(audio_q)
asr = DummyASR("ASR", audio_q, text_q)

# Create the pipeline with the stages
pipeline = Pipeline([mic, asr])

# Start the pipeline
logging.info("Running pipeline... Ctrl+C to stop")
pipeline.start()

try:
    while True:
        if not text_q.empty():
            recognized_text = text_q.get()
            logging.info(f"TEXT: {recognized_text}")
        else:
            # Provide real-time feedback when the pipeline is idle
            logging.debug("Waiting for audio input...")
        time.sleep(0.1)

except KeyboardInterrupt:
    logging.info("Stopping pipeline...")
    pipeline.stop()
    logging.info("Stopped")

except Exception as e:
    logging.error(f"An error occurred: {e}")
    pipeline.stop()
    logging.info("Pipeline stopped due to error.")

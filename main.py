import queue
import time
import logging

from core.pipeline import Pipeline
from audio.mic import MicStage
from asr.vosk_asr import VoskASR

from translate.argos_stage import ArgosStage

from tts.espeak_stage import EspeakStage
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create the audio and text queues
audio_q = queue.Queue(maxsize=50)
text_q = queue.Queue(maxsize=50)
translated_q = queue.Queue(maxsize=50)
# Set up the stages
mic = MicStage(audio_q)
asr = VoskASR(
    input_q=audio_q,
    output_q=text_q,
    model_path="vosk-model-small-hi-0.22"
)
translator = ArgosStage(
    input_q=text_q,
    output_q=translated_q
)

tts = EspeakStage(
    input_q=translated_q
)
# Create the pipeline with the stages
pipeline = Pipeline([mic, asr, translator, tts])

# Start the pipeline
logging.info("Running pipeline... Ctrl+C to stop")
pipeline.start()

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    logging.info("Stopping pipeline...")
    pipeline.stop()
    logging.info("Stopped")

except Exception as e:
    logging.error(f"An error occurred: {e}")
    pipeline.stop()
    logging.info("Pipeline stopped due to error.")

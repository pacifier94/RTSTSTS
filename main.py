import queue
import logging
import time
from core.pipeline import Pipeline
from audio.mic import MicStage
from asr.vosk_asr import VoskASR 
from translator.offline_translator import OfflineTranslatorStage

logging.basicConfig(level=logging.INFO, format='%(message)s')

audio_q = queue.Queue(maxsize=100) # Mic -> ASR
text_q = queue.Queue(maxsize=50)   # ASR -> Translator
trans_q = queue.Queue(maxsize=50)  # Translator -> Main Loop (The missing one!)

mic = MicStage(audio_q, samplerate=16000)
asr = VoskASR(audio_q, text_q, model_path="vosk-model-small-en-in-0.4")
translator = OfflineTranslatorStage(text_q, trans_q, from_code='en', to_code='hi')

pipeline = Pipeline([mic, asr])
logging.info("--- Pipeline Started: Speak into the mic! ---")
pipeline.start()

try:
    while True:
        # 1. ONLY print the final translated result here
        if not trans_q.empty():
            res = trans_q.get()
            print(f"\n" + "="*30)
            print(f"ENGLISH: {res['original']}")
            print(f"HINDI  : {res['translated']}")
            print("="*30 + "\n")
        
        time.sleep(0.01)

except KeyboardInterrupt:
    logging.info("\nShutting down...")
    pipeline.stop()


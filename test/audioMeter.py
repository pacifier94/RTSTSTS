import queue
import time
import logging
import numpy as np
from core.pipeline import Pipeline
from audio.mic import MicStage

# 1. Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("Validator")

# 2. Setup Queues
# Setting a maxsize helps test your "Queue Full" logic
audio_q = queue.Queue(maxsize=10) 

# 3. Initialize Mic
# 16000Hz, blocksize of 1600 = 100ms chunks (standard for streaming)
mic = MicStage(audio_q, samplerate=16000)

# 4. Start Pipeline
pipeline = Pipeline([mic])
logger.info("--- Starting Audio Validation Test ---")
logger.info("Speak into the mic to see the volume meter.")
pipeline.start()

try:
    while True:
        if not audio_q.empty():
            raw_bytes = audio_q.get()
            
            # Convert to integers
            audio_data = np.frombuffer(raw_bytes, dtype=np.int16)
            
            # CALCULATE STATS
            max_val = np.max(np.abs(audio_data))
            mean_val = np.mean(audio_data)
            
            # If max_val is > 0, we ARE getting audio
            if max_val > 0:
                meter = "█" * int(max_val / 500) # Scale for 16-bit sensitivity
                print(f"PEAK: {max_val:<5} | AVG: {mean_val:.2f} | [{meter:<40}]", end="\r")
            else:
                print("SIGNAL DEAD: All samples are zero. Check Mute/Privacy.", end="\r")

        time.sleep(0.01)

except KeyboardInterrupt:
    logger.info("\nStopping validation...")
    pipeline.stop()
    logger.info("Done.")

except Exception as e:
    logger.error(f"\nValidation failed: {e}")
    pipeline.stop()

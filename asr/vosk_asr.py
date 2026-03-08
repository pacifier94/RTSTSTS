import json
import logging
from vosk import Model, KaldiRecognizer
from core.stage import Stage

class VoskASR(Stage):
    def __init__(self, input_q, output_q, model_path):
        super().__init__("ASR", input_q, output_q)
        logging.info(f"Loading ASR model from {model_path}...")
        self.model = Model(model_path)
        # 16000 must match your MicStage target_samplerate
        self.rec = KaldiRecognizer(self.model, 16000)

    def process(self, data):
            if data is None: return None
            
            if self.rec.AcceptWaveform(data):
                res = json.loads(self.rec.Result())
                text = res.get("text", "").strip()
                if text:
                    print(f"\n[DEBUG ASR]: Captured Final: {text}")
                    return {"type": "final", "text": text}
            else:
                part = json.loads(self.rec.PartialResult())
                text = part.get("partial", "").strip()
                if text:
                    return {"type": "partial", "text": text}
            
            # ADD THIS: Check for "FinalResult" even if AcceptWaveform hasn't triggered
            # This helps in noisy environments
            return None
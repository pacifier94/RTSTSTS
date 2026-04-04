import queue
import logging
import threading
import time
import customtkinter as ctk
import os
import sys


from core.pipeline import Pipeline
from audio.mic import MicStage
from asr.vosk_asr import VoskASR
from translate.argos_stage import ArgosStage
from tts.espeak_stage import EspeakStage


def get_base_path():
    """Get the correct path whether running as script or as frozen exe"""
    if getattr(sys, 'frozen', False):
        # Running as EXE
        return sys._MEIPASS
    else:
        # Running as Script
        return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Config
        self.title("Hindi-Bengali Real-Time Bridge")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")
        
        self.running = False 

        # --- UI LAYOUT ---
        self.label_title = ctk.CTkLabel(self, text="🎙️ Live Voice Translator", font=("Arial", 28, "bold"))
        self.label_title.pack(pady=20)

        # Transcript Frames
        self.display_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.display_frame.pack(expand=True, fill="both", padx=30)

        # Hindi Box
        self.hi_box = ctk.CTkTextbox(self.display_frame, width=400, font=("Arial", 16), border_width=2)
        self.hi_box.pack(side="left", expand=True, fill="both", padx=10)
        self.hi_box.insert("0.0", "--- HINDI (What I Hear) ---\n\n")

        # Bengali Box
        self.bn_box = ctk.CTkTextbox(self.display_frame, width=400, font=("Arial", 16), border_width=2, fg_color="#1e1e1e")
        self.bn_box.pack(side="right", expand=True, fill="both", padx=10)
        self.bn_box.insert("0.0", "--- BENGALI (Translation) ---\n\n")

        # Status & Latency Bar
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(pady=10, fill="x", padx=40)

        self.status_var = ctk.StringVar(value="Status: System Ready")
        self.status_label = ctk.CTkLabel(self.info_frame, textvariable=self.status_var, font=("Arial", 13, "italic"), text_color="cyan")
        self.status_label.pack(side="left")

        self.latency_var = ctk.StringVar(value="Latency: 0.0s")
        self.latency_label = ctk.CTkLabel(self.info_frame, textvariable=self.latency_var, font=("Arial", 12), text_color="gray")
        self.latency_label.pack(side="right")

        # Control Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=30)

        self.start_btn = ctk.CTkButton(self.btn_frame, text="Start Translator", command=self.start_system, 
                                       width=200, height=50, font=("Arial", 16, "bold"), fg_color="#2ecc71", hover_color="#27ae60")
        self.start_btn.grid(row=0, column=0, padx=20)

        self.stop_btn = ctk.CTkButton(self.btn_frame, text="Stop / Clear", command=self.stop_system, 
                                      width=200, height=50, font=("Arial", 16, "bold"), fg_color="#e74c3c", hover_color="#c0392b")
        self.stop_btn.grid(row=0, column=1, padx=20)

    def setup_pipeline(self):
        """Initializes queues and stages with UI callback"""
        self.audio_q = queue.Queue(maxsize=200)
        self.text_q = queue.Queue(maxsize=50)
        self.translated_q = queue.Queue(maxsize=50)

        self.mic = MicStage(self.audio_q)
        self.asr = VoskASR(self.audio_q, self.text_q, "vosk-model-small-hi-0.22")
        
        # Link UI trigger
        self.translator = ArgosStage(
            input_q=self.text_q, 
            output_q=self.translated_q,
            ui_callback=self.trigger_ui_update
        )

        self.tts = EspeakStage(input_q=self.translated_q)
        self.pipeline = Pipeline([self.mic, self.asr, self.translator, self.tts])

    def trigger_ui_update(self, hi, bn, ts=None):
        """Thread-safe bridge to update UI and calculate latency"""
        latency = 0
        if ts:
            latency = time.time() - ts
        self.after(0, self._update_ui_content, hi, bn, latency)

    def _update_ui_content(self, hi, bn, latency):
        if hi == "ERROR":
            self.status_var.set(f"❌ Error: {bn}")
            return

        # Append to boxes
        self.hi_box.insert("end", f"🎤 {hi}\n")
        self.bn_box.insert("end", f"🇧🇩 {bn}\n\n")
        
        # Auto-scroll
        self.hi_box.see("end")
        self.bn_box.see("end")
        
        # Update Meta Info
        self.status_var.set(f"Status: 🎤 Listening... (Last: {time.strftime('%H:%M:%S')})")
        self.latency_var.set(f"Latency: {latency:.2f}s")

    def start_system(self):
        if self.running:
            return
        
        self.status_var.set("⏳ Status: Loading Models & Warming Up...")
        self.start_btn.configure(state="disabled")
        
        # Run init in background so UI doesn't hang
        def async_init():
            try:
                self.setup_pipeline()
                self.running = True
                self.pipeline.start()
                self.after(0, lambda: self.status_var.set("Status: 🎤 Listening..."))
            except Exception as e:
                self.after(0, lambda: self.status_var.set(f"❌ Initialization Failed: {str(e)}"))
                self.after(0, lambda: self.start_btn.configure(state="normal"))

        threading.Thread(target=async_init, daemon=True).start()

    def stop_system(self):
        if hasattr(self, 'pipeline'):
            self.pipeline.stop()
            time.sleep(0.5) # Allow threads to close
        
        self.running = False
        self.status_var.set("Status: Stopped")
        self.start_btn.configure(state="normal")
        
        # Clean transcript for next run
        self.hi_box.delete("3.0", "end")
        self.bn_box.delete("3.0", "end")

if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()

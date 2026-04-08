import queue
import logging
import threading
import time
import customtkinter as ctk
import os
import sys
from collections import deque

from core.pipeline import Pipeline
from audio.mic import MicStage
from asr.vosk_asr import VoskASR
from translate.argos_stage import ArgosStage
from tts.espeak_stage import EspeakStage


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Hindi → Bengali Translator")
        self.geometry("1100x900")
        ctk.set_appearance_mode("dark")

        self.running = False
        self.audio_level = 0
        self.threshold = 0.02   # default noise threshold

        # ---------------- HEADER ----------------
        self.header = ctk.CTkFrame(self, fg_color="#020617")
        self.header.pack(fill="x")

        ctk.CTkLabel(
            self.header,
            text="🎙️ Real-Time Speech Translator",
            font=("Arial", 30, "bold"),
            text_color="#38bdf8"
        ).pack(pady=(10, 5))

        # Mic indicator
        self.mic_indicator = ctk.CTkLabel(
            self.header,
            text="● LIVE",
            font=("Arial", 14, "bold"),
            text_color="gray"
        )
        self.mic_indicator.pack()

        self.blink_state = True
        self.after(500, self.blink_mic)

        # ---------------- SLIDER ----------------
        self.slider_frame = ctk.CTkFrame(self)
        self.slider_frame.pack(pady=5)

        ctk.CTkLabel(self.slider_frame, text="Noise Threshold").pack()

        self.slider = ctk.CTkSlider(
            self.slider_frame,
            from_=0.005,
            to=0.1,
            command=self.update_threshold
        )
        self.slider.set(self.threshold)
        self.slider.pack()

        # ---------------- DISPLAY ----------------
        self.display_frame = ctk.CTkFrame(self)
        self.display_frame.pack(expand=True, fill="both", padx=20, pady=10)

        self.hi_box = ctk.CTkTextbox(self.display_frame)
        self.hi_box.pack(side="left", expand=True, fill="both", padx=10)

        self.bn_box = ctk.CTkTextbox(self.display_frame)
        self.bn_box.pack(side="right", expand=True, fill="both", padx=10)

        # ---------------- WAVEFORM ----------------
        self.wave_canvas = ctk.CTkCanvas(self, height=80, bg="#020617")
        self.wave_canvas.pack(fill="x", padx=20)

        self.wave_data = deque([0]*50, maxlen=50)
        self.after(50, self.update_waveform)

        # ---------------- STATUS ----------------
        self.status_var = ctk.StringVar(value="● Ready")
        ctk.CTkLabel(self, textvariable=self.status_var).pack()

        # ---------------- BUTTONS ----------------
        self.start_btn = ctk.CTkButton(self, text="Start", command=self.start_system)
        self.start_btn.pack(pady=5)

        self.stop_btn = ctk.CTkButton(self, text="Stop", command=self.stop_system)
        self.stop_btn.pack(pady=5)

    # -------- MIC CALLBACK --------
    def update_audio_level(self, level):
        self.audio_level = level

    # -------- THRESHOLD --------
    def update_threshold(self, val):
        self.threshold = float(val)

    # -------- PIPELINE --------
    def setup_pipeline(self):
        self.audio_q = queue.Queue()
        self.text_q = queue.Queue()
        self.translated_q = queue.Queue()

        self.mic = MicStage(self.audio_q, ui_callback=self.update_audio_level)
        self.asr = VoskASR(self.audio_q, self.text_q, "vosk-model-small-hi-0.22")

        self.translator = ArgosStage(self.text_q, self.translated_q, self.trigger_ui_update)
        self.tts = EspeakStage(self.translated_q)

        self.pipeline = Pipeline([self.mic, self.asr, self.translator, self.tts])

    # -------- UI UPDATE --------
    def trigger_ui_update(self, hi, bn, ts=None):
        if self.audio_level < self.threshold:
            return  # ignore silence

        self.after(0, self._update_ui, hi, bn)

    def _update_ui(self, hi, bn):
        self.hi_box.insert("end", f"{hi}\n")
        self.bn_box.insert("end", f"{bn}\n\n")

        self.hi_box.see("end")
        self.bn_box.see("end")

        self.status_var.set("● Speaking detected")

    # -------- WAVEFORM --------
    def update_waveform(self):
        if self.audio_level > self.threshold:
            level = min(self.audio_level * 600, 70)
        else:
            level = 0

        self.wave_data.append(level)

        self.wave_canvas.delete("all")
        w = self.wave_canvas.winfo_width()
        step = w / len(self.wave_data)

        for i, v in enumerate(self.wave_data):
            x = i * step
            self.wave_canvas.create_line(x, 40-v/2, x, 40+v/2, fill="#22d3ee", width=2)

        self.after(50, self.update_waveform)

    # -------- MIC BLINK --------
    def blink_mic(self):
        color = "red" if self.running and self.blink_state else "gray"
        self.mic_indicator.configure(text_color=color)
        self.blink_state = not self.blink_state
        self.after(500, self.blink_mic)

    # -------- CONTROLS --------
    def start_system(self):
        if self.running:
            return

        def init():
            self.setup_pipeline()
            self.pipeline.start()
            self.running = True
            self.after(0, lambda: self.status_var.set("● Listening"))

        threading.Thread(target=init, daemon=True).start()

    def stop_system(self):
        if hasattr(self, "pipeline"):
            self.pipeline.stop()

        self.running = False
        self.status_var.set("● Stopped")


if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()

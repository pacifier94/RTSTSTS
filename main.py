import queue
import logging
import threading
import time
import customtkinter as ctk
import os
import sys
import random
from collections import deque

from core.pipeline import Pipeline
from audio.mic import MicStage
from asr.vosk_asr import VoskASR
from translate.argos_stage import ArgosStage
from tts.espeak_stage import EspeakStage


def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ---------------- WINDOW ----------------
        self.title("Hindi → Bengali Translator")
        self.geometry("1100x900")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.running = False

        # ---------------- HEADER ----------------
        self.header = ctk.CTkFrame(self, fg_color="#020617")
        self.header.pack(fill="x")

        ctk.CTkLabel(
            self.header,
            text="Real-Time Speech Translator",
            font=("Arial", 32, "bold"),
            text_color="#38bdf8"
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            self.header,
            text="Hindi → Bengali | Offline | Streaming System",
            font=("Arial", 14),
            text_color="#94a3b8"
        ).pack()

        # LIVE badge
        self.mic_indicator = ctk.CTkLabel(
            self.header,
            text="● LIVE",
            font=("Arial", 14, "bold"),
            text_color="gray"
        )
        self.mic_indicator.pack(pady=(5, 10))

        self.blink_state = True
        self.after(500, self.blink_mic)

        # ---------------- LANG SELECT ----------------
        self.lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.lang_frame.pack(pady=10)

        self.source_lang = ctk.CTkOptionMenu(self.lang_frame, values=["Hindi"])
        self.source_lang.set("Hindi")
        self.source_lang.pack(side="left", padx=10)

        self.target_lang = ctk.CTkOptionMenu(self.lang_frame, values=["Bengali"])
        self.target_lang.set("Bengali")
        self.target_lang.pack(side="left", padx=10)

        # ---------------- DISPLAY ----------------
        self.display_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.display_frame.pack(expand=True, fill="both", padx=20)

        self.hi_panel = self.create_card(self.display_frame, "#1e293b")
        self.hi_panel.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        self.bn_panel = self.create_card(self.display_frame, "#1e293b")
        self.bn_panel.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        # Titles
        ctk.CTkLabel(self.hi_panel, text="🇮🇳 Hindi Input", font=("Arial", 18, "bold"), text_color="#facc15").pack(pady=10)
        ctk.CTkLabel(self.bn_panel, text="🇧🇩 Bengali Output", font=("Arial", 18, "bold"), text_color="#4ade80").pack(pady=10)

        # Textboxes
        self.hi_box = ctk.CTkTextbox(self.hi_panel, fg_color="#020617", text_color="#e2e8f0")
        self.hi_box.pack(expand=True, fill="both", padx=10, pady=10)

        self.bn_box = ctk.CTkTextbox(self.bn_panel, fg_color="#020617", text_color="#e2e8f0")
        self.bn_box.pack(expand=True, fill="both", padx=10, pady=10)

        # ---------------- WAVEFORM ----------------
        self.wave_canvas = ctk.CTkCanvas(self, height=80, bg="#020617", highlightthickness=0)
        self.wave_canvas.pack(fill="x", padx=20)

        self.wave_data = deque([0]*60, maxlen=60)
        self.after(100, self.update_waveform)

        # ---------------- LATENCY GRAPH ----------------
        self.latency_canvas = ctk.CTkCanvas(self, height=100, bg="#020617", highlightthickness=0)
        self.latency_canvas.pack(fill="x", padx=20, pady=5)

        self.latency_history = deque([0]*40, maxlen=40)
        self.after(200, self.update_latency_graph)

        # ---------------- STATUS ----------------
        self.status_frame = ctk.CTkFrame(self, fg_color="#020617")
        self.status_frame.pack(fill="x", padx=20, pady=10)

        self.status_var = ctk.StringVar(value="Ready")
        ctk.CTkLabel(self.status_frame, textvariable=self.status_var, text_color="#22c55e").pack(side="left", padx=10)

        self.latency_var = ctk.StringVar(value="Latency: 0.00s")
        ctk.CTkLabel(self.status_frame, textvariable=self.latency_var, text_color="#94a3b8").pack(side="right", padx=10)

        # ---------------- BUTTONS ----------------
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=15)

        self.start_btn = ctk.CTkButton(self.btn_frame, text="▶ Start", command=self.start_system,
                                       fg_color="#22c55e", hover_color="#16a34a")
        self.start_btn.grid(row=0, column=0, padx=10)

        self.stop_btn = ctk.CTkButton(self.btn_frame, text="■ Stop", command=self.stop_system,
                                      fg_color="#ef4444", hover_color="#dc2626")
        self.stop_btn.grid(row=0, column=1, padx=10)

        self.clear_btn = ctk.CTkButton(self.btn_frame, text="🧹 Clear", command=self.clear_text,
                                       fg_color="#334155", hover_color="#1e293b")
        self.clear_btn.grid(row=0, column=2, padx=10)

    # -------- CARD STYLE --------
    def create_card(self, parent, color):
        return ctk.CTkFrame(parent, fg_color=color, corner_radius=20)

    # -------- PIPELINE --------
    def setup_pipeline(self):
        self.audio_q = queue.Queue()
        self.text_q = queue.Queue()
        self.translated_q = queue.Queue()

        self.mic = MicStage(self.audio_q)
        self.asr = VoskASR(self.audio_q, self.text_q, "vosk-model-small-hi-0.22")

        self.translator = ArgosStage(self.text_q, self.translated_q, self.trigger_ui_update)
        self.tts = EspeakStage(self.translated_q)

        self.pipeline = Pipeline([self.mic, self.asr, self.translator, self.tts])

    # -------- UI UPDATE --------
    def trigger_ui_update(self, hi, bn, ts=None):
        latency = time.time() - ts if ts else 0
        self.after(0, self._update_ui, hi, bn, latency)

    def _update_ui(self, hi, bn, latency):
        self.hi_box.insert("end", f"🗣 {hi}\n")
        self.bn_box.insert("end", f"🔊 {bn}\n\n")

        self.hi_box.see("end")
        self.bn_box.see("end")

        self.status_var.set("Listening")
        self.latency_var.set(f"Latency: {latency:.2f}s")

        self.latency_history.append(latency)

    # -------- VISUALS --------
    def blink_mic(self):
        color = "#ef4444" if self.running and self.blink_state else "#64748b"
        self.mic_indicator.configure(text_color=color)
        self.blink_state = not self.blink_state
        self.after(500, self.blink_mic)

    def update_waveform(self):
        val = random.randint(10, 70) if self.running else 0
        self.wave_data.append(val)

        self.wave_canvas.delete("all")
        w = self.wave_canvas.winfo_width()
        step = w / len(self.wave_data)

        for i, v in enumerate(self.wave_data):
            x = i * step
            self.wave_canvas.create_line(x, 40-v/2, x, 40+v/2, fill="#22d3ee", width=2)

        self.after(100, self.update_waveform)

    def update_latency_graph(self):
        self.latency_canvas.delete("all")
        w = self.latency_canvas.winfo_width()
        h = 100
        step = w / len(self.latency_history)

        for i in range(len(self.latency_history)-1):
            x1 = i * step
            x2 = (i+1) * step
            y1 = h - self.latency_history[i]*50
            y2 = h - self.latency_history[i+1]*50
            self.latency_canvas.create_line(x1, y1, x2, y2, fill="#60a5fa", width=2)

        self.after(200, self.update_latency_graph)

    # -------- CONTROLS --------
    def start_system(self):
        if self.running:
            return

        self.status_var.set("Loading...")
        self.start_btn.configure(state="disabled")

        def init():
            try:
                self.setup_pipeline()
                self.pipeline.start()
                self.running = True
                self.after(0, lambda: self.status_var.set("Listening"))
            except Exception as e:
                self.after(0, lambda: self.status_var.set(f"Error: {e}"))

        threading.Thread(target=init, daemon=True).start()

    def stop_system(self):
        if hasattr(self, "pipeline"):
            self.pipeline.stop()

        self.running = False
        self.status_var.set("Stopped")
        self.start_btn.configure(state="normal")

    def clear_text(self):
        self.hi_box.delete("0.0", "end")
        self.bn_box.delete("0.0", "end")


if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()

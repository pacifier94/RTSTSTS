# Real-Time Speech-to-Speech Translation Pipeline

A modular real-time speech translation system that converts live microphone input into translated speech output using a streaming, concurrent pipeline architecture.

## Core Design Philosophy

The system is built around three principles:

* **Streaming first** — all components process data continuously
* **Concurrent execution** — each module runs independently
* **Loose coupling** — stages communicate only through queues

Every module follows the same contract:

```
input → process → output
```

This makes the system extensible, testable, and easy to debug.

---


## Repository Structure

```
speech-pipeline/
│
├── core/
│   ├── stage.py        # Base stage class for all modules
│   ├── pipeline.py     # Pipeline controller
│
├── audio/
│   └── mic.py          # Microphone streaming input
│
├── asr/
│   └── dummy_asr.py    # Placeholder recognizer
│
└── main.py             # Entry point
```

---

## How the Pipeline Works

Each processing unit is implemented as a **Stage** thread:

* reads from input queue
* processes data
* writes to output queue

The pipeline controller simply starts and stops all stages.

Because stages do not depend on each other directly, they can be replaced or upgraded independently.

---

## Running the Project

### Install Dependencies

```
pip install sounddevice
```

---

### Run

```
python main.py
```

Expected output:

```
Running pipeline...
TEXT: recognized speech chunk
TEXT: recognized speech chunk
```

---

## Development Roadmap

The system will be expanded incrementally to maintain stability.

---

### Phase 1 — Infrastructure

* Pipeline engine
* Threaded stages
* Streaming queues
* Microphone capture
* Dummy recognizer

---

### Phase 2 — Real Speech Recognition

Replace dummy recognizer with real streaming ASR:

Recommended options:

* Vosk (offline, lightweight)
* Whisper streaming
* DeepSpeech

---

### Phase 3 — Translation Stage

Add translation module:

```
Mic → ASR → Translation → Console
```

Requirements:

* incremental translation
* revision handling
* low latency

---

### Phase 4 — Speech Synthesis

Add TTS module:

```
Mic → ASR → Translation → TTS → Speaker
```

Requirements:

* real-time audio playback
* buffering
* smooth streaming

---

### Phase 5 — Dashboard

Add live system monitor showing:

* audio activity
* partial transcripts
* translation updates
* per-stage latency
* pipeline health

---

### Phase 6 — Optimization

Final system improvements:

* latency tuning
* concurrency optimization
* queue sizing
* stability testing
* stress testing

---

## Why This Architecture?

Real-time speech systems fail most often because of poor pipeline design, not model accuracy.

This architecture ensures:

* non-blocking execution
* predictable latency
* independent module testing
* easy debugging
* flexible upgrades

---


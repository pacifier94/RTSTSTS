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

## System Design

The system operates as a modular pipeline where each processing stage is independent. Each stage can be replaced, modified, or upgraded without affecting others, ensuring ease of development and extensibility.

Pipeline Architecture

```
[Mic] → [ASR] → [Translation] → [TTS] → [Speaker]
```

1. **Microphone Input (Mic)**:
   - Captures raw audio continuously.
   - Provides data to ASR in real-time.

2. **Automatic Speech Recognition (ASR)**:
   - Converts speech to text using streaming models (e.g., Vosk, Whisper, or DeepSpeech).
   - Outputs transcribed text, which is sent to the Translation stage.

3. **Translation**:
   - Translates text from source language to the target language.
   - Outputs translated text to TTS.
   - Ensure the translation system is optimized for low-latency, incremental processing.

4. **Text-to-Speech (TTS)**:
   - Converts translated text into speech.
   - Audio is buffered and streamed to the speaker.

5. **Speaker Output**:
   - Plays the translated speech to the user in real-time.
   - Audio playback is continuous, even if the translation and synthesis are still processing.

Each of these stages operates in parallel, reading from an input queue, processing the data, and writing to an output queue.


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

## Technical Considerations
# Latency
The system needs to minimize latency at each stage to enable near real-time communication. Optimizations will be implemented at the queue level and within the stages to balance throughput and response time.

# Concurrency
To handle real-time processing, each stage will run in its own thread, with communication via thread-safe queues. Proper synchronization mechanisms will be used to avoid race conditions.

# Fault Tolerance
The system should handle failure gracefully. For example:
  If the ASR module fails, it should fall back to a backup recognizer or output a failure message.
  The pipeline should allow dynamic stage replacement without restarting the entire system.


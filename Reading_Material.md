## Related Research & Reading List — Real-Time Speech-to-Speech Translation

Below are key research papers and implementation references that informed the design and architecture of this project. 

### 1. Direct Speech to Speech Translation: A Review
Survey paper covering both cascaded pipelines (ASR→MT→TTS) and direct neural speech-to-speech systems. Discusses architectural trade-offs, latency issues, and challenges in building real-time S2ST systems. Useful for understanding the research landscape and motivating system design choices.  
🔗 https://arxiv.org/abs/2503.04799

---

### 2. SimulTron: On-Device Simultaneous Speech to Speech Translation
Introduces a lightweight architecture for real-time speech translation running entirely on device. Focuses on reducing latency while maintaining translation quality, making it highly relevant for offline and real-time deployment constraints.  
🔗 https://arxiv.org/pdf/2406.02133

---

### 3. Spoken Language Translation Pipelines for Conversations
Evaluates multiple ASR→MT→TTS pipeline combinations in conversational settings. Analyzes trade-offs between latency and translation accuracy and discusses pipeline design decisions that affect streaming performance.  
🔗 https://arxiv.org/abs/2506.01406

---

### 4. Learning When to Speak: Latency & Quality Trade-offs for Real-Time Speech Translation
Focuses on simultaneous translation strategies and explores policies for deciding when a system should begin speaking translated output before full input is received. Helps understand latency-quality balancing techniques.  
🔗 https://www.isca-speech.org/archive/interspeech_2023/dugan23_interspeech.pdf

---

### 5. Real-Time Multilingual Speech Translation for Peer Communication
A practical implementation-focused study demonstrating a real-time speech translation system across multiple languages. Provides useful insights into architecture, integration challenges, and real-world system behavior.  
🔗 https://www.researchgate.net/publication/393081843_Real-Time_Multilingual_Speech_Translation_for_Peer_Communication

---

### 6. Real-Time Spoken Language Translator Using Machine Learning
Describes a working real-time translation pipeline using machine learning components. Useful for understanding system-level integration and implementation considerations in real-time scenarios.  
🔗 https://www.ijert.org/real-time-spoken-language-translator-using-machine-learning

---

### 7. Cascaded ASR–MT–TTS for Real-Time Voice Translation
Explains traditional cascaded speech translation architecture and discusses design requirements for making such systems usable in real time. Helpful for comparing classical and modern approaches.  
🔗 https://www.ijmrset.com/upload/49_CASCADED_ASR-MT-TTS_FOR_REAL-TIME_VOICE_AND_DOCUMENT_TRANSLATION.pdf

---

### 8. Offline Speech Translation Systems: Technologies and Prospects
Although focused on offline systems, this review explains core challenges in integrating ASR, translation, and synthesis modules. Provides strong conceptual background for designing real-time pipelines.  
🔗 https://www.ijfmr.com/papers/2025/6/62449.pdf

---

##  How These Papers Will Help In Building This Project

These references collectively support:

- Understanding real-time speech translation architectures
- Designing low-latency streaming pipelines
- Handling partial and revised outputs
- Evaluating trade-offs between latency and accuracy
- Choosing between cascaded vs end-to-end approaches
- Building observable and measurable real-time systems

They serve as both conceptual foundations and practical implementation references for this system.

---

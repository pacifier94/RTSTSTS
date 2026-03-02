import sounddevice as sd
print(sd.query_devices())
print(f"Default Input Device: {sd.default.device[0]}")

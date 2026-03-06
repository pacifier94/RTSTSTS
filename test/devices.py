import sounddevice as sd

# list all the devices connected to our system
print(sd.query_devices())
print(f"Default Input Device: {sd.default.device[0]}")

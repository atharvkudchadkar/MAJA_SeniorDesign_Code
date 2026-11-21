# import requests
# import wave

# # Read only the raw audio bytes (the "dots") from beep.wav, without the header.
# # This mimics what the ESP32 will send.
# with wave.open("beep.wav", "rb") as f:
#     raw = f.readframes(f.getnframes())

# print(f"Sending {len(raw)} bytes...")

# # Send them to the server, with the language in the URL
# r = requests.post("http://localhost:5000/audio?lang=es", data=raw)

# print("Status code:", r.status_code)   # 200 means success
# print("Server replied:", r.text)       # should say "completed"

import requests
import wave
import numpy as np

# 1. Read the Spanish speech Piper made (22,050 Hz)
with wave.open("tts_test.wav", "rb") as f:
    in_rate = f.getframerate()
    raw = f.readframes(f.getnframes())

# 2. Convert it to 16,000 Hz, like the ESP32 mic will send
samples = np.frombuffer(raw, dtype=np.int16)
new_length = int(len(samples) * 16000 / in_rate)
old_positions = np.linspace(0, len(samples) - 1, new_length)
resampled = np.interp(old_positions, np.arange(len(samples)), samples)
raw_16k = resampled.astype(np.int16).tobytes()

print(f"Sending {len(raw_16k)} bytes ({len(raw_16k) / 2 / 16000:.2f} s)...")

# 3. Send it: Spanish in, French out
r = requests.post("http://localhost:5000/audio?src=es&tgt=fr", data=raw_16k)
print("Status code:", r.status_code)

# 4. Save the reply audio so we can listen to it
if r.status_code == 200:
    with wave.open("reply.wav", "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(22050)
        f.writeframes(r.content)
    print("Saved reply.wav")
else:
    print("Server said:", r.text)
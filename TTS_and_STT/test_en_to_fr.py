# Test case: English speech in, French speech out.
# Run the server first (python hardware.py), then: python test_en_to_fr.py

import requests
import wave
import numpy as np
from tts import TTS, output_rate

SENTENCE = "Hello, how are you today?"
SRC = "en"
TGT = "fr"

# 1. Make the "person speaking": English speech from Piper (22,050 Hz)
speech = TTS(SENTENCE, SRC)
if speech is None:
    raise SystemExit(f"Couldn't make test audio. Is there a '{SRC}' voice in tts.py?")

# 2. Convert it to 16,000 Hz, like the ESP32 mic will send
samples = np.frombuffer(speech, dtype=np.int16)
new_length = int(len(samples) * 16000 / output_rate)
old_positions = np.linspace(0, len(samples) - 1, new_length)
resampled = np.interp(old_positions, np.arange(len(samples)), samples)
raw_16k = resampled.astype(np.int16).tobytes()

print(f"Input:  '{SENTENCE}' ({SRC}), {len(raw_16k) / 2 / 16000:.2f} s")

# 3. Send it to the server
r = requests.post(f"http://localhost:5000/audio?src={SRC}&tgt={TGT}", data=raw_16k)
print("Status code:", r.status_code)

# 4. Save the reply so we can listen
if r.status_code == 200:
    with wave.open("reply_en_to_fr.wav", "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(output_rate)
        f.writeframes(r.content)
    print(f"Saved reply_en_to_fr.wav ({len(r.content) / 2 / output_rate:.2f} s)")
else:
    print("Server said:", r.text)
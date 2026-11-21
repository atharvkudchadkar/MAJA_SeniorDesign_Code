import wave
from piper import PiperVoice

# 1. Load the Spanish voice (the .onnx file in this folder)
voice = PiperVoice.load("es_ES-davefx-medium.onnx")

# 2. Turn a sentence into speech and save it as a WAV
with wave.open("test.wav", "wb") as wav_file:
    voice.synthesize_wav("Hola, ¿cómo estás?", wav_file)

print("Saved test.wav")

# 3. Reopen the WAV and print its settings
with wave.open("test.wav", "rb") as f:
    print("Sample rate:", f.getframerate())   # samples per second
    print("Channels:", f.getnchannels())      # 1 = mono
    print("Sample width:", f.getsampwidth())  # bytes per sample (2 = 16-bit)
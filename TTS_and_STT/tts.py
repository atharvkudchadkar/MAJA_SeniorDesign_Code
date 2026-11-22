# This file turns translated text into speech audio for the ESP32

from piper import PiperVoice
import wave

output_rate = 22050

Voices = {
    "es": PiperVoice.load("es_ES-davefx-medium.onnx"),
    "fr": PiperVoice.load("fr_FR-siwis-medium.onnx"),
    "pt": PiperVoice.load("pt_PT-tugao-medium.onnx"),
    "en": PiperVoice.load("en_US-joe-medium.onnx")
}

def TTS(text, language):
    text = text.strip()
    if text == "":
        print("No text provided")
        return None

    if language not in Voices:
        print(f"No voice for language '{language}'")
        return
    
    voice = Voices[language]

    audio = b""

    for block in voice.synthesize(text):
        audio += block.audio_int16_bytes

    return audio

if __name__ == "__main__":
    #TTS("", "es")
    audio = TTS(" hola, cómo estás ", "es")
    #TTS("bien et toi", "fr")
    print(f"Got {len(audio)} bytes = {len(audio) / 2 / output_rate:.2f} seconds")

    with wave.open("tts_test.wav", "wb") as a:
        a.setnchannels(1)
        a.setsampwidth(2)
        a.setframerate(output_rate)
        a.writeframes(audio)

    print("Saved tts_test.wav file")
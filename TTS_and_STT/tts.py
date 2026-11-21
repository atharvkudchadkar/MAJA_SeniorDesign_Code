# This file turns translated text into speech audio for the ESP32 to play

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





# from gtts import gTTS
# import pygame
# import time

# def TTS(text, lang):
#     text = text.strip()
#     if text == "":
#         print("No text provided")
#         return
#     speech = gTTS(text=text, lang=lang)
#     speech.save("testTTS.mp3")
#     pygame.mixer.init()
#     pygame.mixer.music.load("testTTS.mp3")
#     pygame.mixer.music.play()
#     while pygame.mixer.music.get_busy():
#         time.sleep(0.01)
#     pygame.mixer.music.unload()

# if __name__ == "__main__":
#     #TTS("", "es")
#     TTS(" hola, cómo estás ", "es")
#     #TTS("bien et toi", "fr")
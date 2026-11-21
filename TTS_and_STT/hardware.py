# import math
# import struct
# import wave

# SAMPLE_RATE = 16000
# FREQ = 640
# DURATION = 1
# VOLUME = 10000

# samples = b""

# for i in range(SAMPLE_RATE * DURATION):   # 16,000 samples/sec × 1 sec = 16,000 samples
#     t = i / SAMPLE_RATE
#     value = int(VOLUME * math.sin(2 * math.pi * FREQ * t))
#     samples += struct.pack("<h", value)

# with wave.open("beep.wav", "wb") as f:
#     f.setnchannels(1)              # mono: one microphone
#     f.setsampwidth(2)              # 16 bits = 2 bytes per sample
#     f.setframerate(SAMPLE_RATE)    # 16000 samples per second
#     f.writeframes(samples)


from flask import Flask, request, Response
import wave
from tts import TTS
from stt import transcribe
from translate import translate

app = Flask(__name__)

S_rate = 16000
@app.route("/audio", methods=["POST"])
def receive_audio():
    bytes_data = request.data
    src_lang = request.args.get("src")
    out_lang = request.args.get("tgt")

    print(f"Received {len(bytes_data)} bytes, {src_lang} --> {out_lang}.")

    with wave.open("audio.wav", "wb") as a:
        a.setnchannels(1)
        a.setsampwidth(2)
        a.setframerate(S_rate)
        a.writeframes(bytes_data)


    transcribed_text = transcribe("audio.wav", src_lang)
    if transcribed_text == "":
        return "no speech was detected", 400

    translated_text = translate(transcribed_text, out_lang, src_lang)
    if translated_text is None:
        return "Translation error", 502
    
    print(f"Translated: {translated_text}")

    audio = TTS(translated_text, out_lang)
    if audio is None:
        return "TTS Error", 500

    return Response(audio, mimetype="application/octet-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 5000)

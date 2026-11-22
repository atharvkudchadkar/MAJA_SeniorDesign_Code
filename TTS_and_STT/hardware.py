from flask import Flask, request, Response
from datetime import datetime
import wave
import struct
import math
import traceback

from tts import TTS
from stt import transcribe
from translate import translate

app = Flask(__name__)

S_rate = 16000


# this is to help debug

def describe_audio(data, sample_rate=S_rate):
    """Print a quick health check of raw 16-bit mono PCM."""
    print(f"  [audio] first 16 bytes: {data[:16].hex(' ')}")
    if data[:4] == b"RIFF":
        print("  [audio] ⚠ data already has a WAV header -> double header! stripping 44 bytes")
        data = data[44:]

    n = len(data) // 2
    if n == 0:
        print("  [audio] ⚠ no samples")
        return data

    s = struct.unpack("<%dh" % n, data[:n * 2])
    peak = max(abs(x) for x in s)
    rms = math.sqrt(sum(x * x for x in s) / n)
    db = 20 * math.log10(rms / 32768) if rms > 0 else -120.0
    zeros = sum(1 for x in s if x == 0) / n * 100

    print(f"  [audio] {n} samples = {n / sample_rate:.2f}s @ {sample_rate} Hz")
    print(f"  [audio] peak={peak}  rms={rms:.0f}  level={db:.1f} dBFS  zeros={zeros:.0f}%")

    if peak == 0:
        print("  [audio] ⚠ ALL ZEROS: mic sends nothing (check L/R pin, channel fmt, wiring)")
    elif peak < 200:
        print("  [audio] ⚠ NEARLY SILENT: likely 32->16 bit shift issue on ESP")
    elif peak >= 32000:
        print("  [audio] ⚠ CLIPPING: reduce the bit shift / gain on ESP")
    elif zeros > 40:
        print("  [audio] ⚠ many zero samples: maybe stereo/32-bit data read as 16-bit mono")
    else:
        print("  [audio] ✓ signal level looks OK")
    return data


@app.route("/audio", methods=["POST"])
def receive_audio():
    print("\n========== Incoming recording ==========")
    bytes_data = request.data
    src_lang = request.args.get("src")
    out_lang = request.args.get("tgt")

    print(f"  [req] Content-Length header: {request.content_length}")
    print(f"  [req] Received {len(bytes_data)} bytes, {src_lang} --> {out_lang}")
    if not src_lang or not out_lang:
        print("  [req] ⚠ missing src/tgt query params")

    bytes_data = describe_audio(bytes_data)

    filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.wav"
    with wave.open(filename, "wb") as a:
        a.setnchannels(1)
        a.setsampwidth(2)
        a.setframerate(S_rate)
        a.writeframes(bytes_data)
    print(f"  [file] Saved: {filename}")

    try:
        transcribed_text = transcribe(filename, src_lang)
    except Exception:
        print("  [stt] ✗ transcribe() crashed:")
        traceback.print_exc()
        return "STT error", 500
    print(f"  [stt] Heard: {transcribed_text!r}")
    if not transcribed_text or transcribed_text.strip() == "":
        print("  [stt] ⚠ no speech detected")
        return "no speech was detected", 400

    try:
        translated_text = translate(transcribed_text, out_lang, src_lang)
    except Exception:
        print("  [translate] ✗ translate() crashed:")
        traceback.print_exc()
        return "Translation error", 502
    print(f"  [translate] Translated: {translated_text!r}")
    if translated_text is None:
        return "Translation error", 502

    try:
        audio = TTS(translated_text, out_lang)
    except Exception:
        print("  [tts] ✗ TTS() crashed:")
        traceback.print_exc()
        return "TTS Error", 500
    if audio is None:
        print("  [tts] ✗ TTS returned None")
        return "TTS Error", 500
    print(f"  [tts] Returning {len(audio)} bytes of audio")
    print("========================================")

    return Response(audio, mimetype="application/octet-stream")


@app.route("/ping")
def ping():
    return "pong"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)




































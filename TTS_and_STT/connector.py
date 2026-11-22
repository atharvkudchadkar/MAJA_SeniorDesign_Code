from http.server import BaseHTTPRequestHandler, HTTPServer
import wave
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000

SAMPLE_RATE = 16000


class AudioReceiver(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path != "/audio":
            self.send_error(404)
            return

        length = int(
            self.headers.get("Content-Length", "0")
        )

        source = self.headers.get(
            "X-Source-Language", "Unknown"
        )

        target = self.headers.get(
            "X-Target-Language", "Unknown"
        )

        print("\nIncoming recording")
        print("Translation:", source, "->", target)
        print("Expected bytes:", length)

        if length <= 0 or length > 2_000_000:
            self.send_error(400, "Invalid audio size")
            return

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        filename = "recording_" + timestamp + ".wav"

        remaining = length

        with wave.open(filename, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)

            while remaining > 0:
                chunk = self.rfile.read(
                    min(4096, remaining)
                )

                if not chunk:
                    break

                wav.writeframesraw(chunk)
                remaining -= len(chunk)

        if remaining != 0:
            print("Incomplete recording received")
            self.send_error(400, "Incomplete upload")
            return

        print("Saved:", filename)
        print("Received bytes:", length)

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"OK")


server = HTTPServer((HOST, PORT), AudioReceiver)

print("Audio receiver running on port", PORT)
print("Waiting for ESP32 recordings...")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nStopping server")
finally:
    server.server_close()
import pyaudio
import struct
import math


THRESHOLD = 0.06
CHUNK = 1024
RATE = 16000


def is_speech_present(stream, chunk: int = CHUNK, rate: int = RATE, threshold: float = THRESHOLD) -> bool:
    """Very lightweight microphone activity detector for a wake-word prototype."""
    data = stream.read(chunk)
    # Convert bytes to 16-bit samples
    samples = struct.unpack("%dh" % (len(data) // 2), data)
    rms = math.sqrt(sum(sample * sample for sample in samples) / len(samples)) / 32768.0
    return rms > threshold


def listen_for_wake_word():
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Listening for voice activity...")
    try:
        while True:
            if is_speech_present(stream):
                print("Wake-word candidate detected. Voice activity found.")
                return True
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()


if __name__ == "__main__":
    listen_for_wake_word()

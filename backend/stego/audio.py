from pydub import AudioSegment
import numpy as np
import wave
import os
import uuid

def encode_audio(input_audio_path: str, message: str, output_audio_path: str) -> None:
    # Only supports WAV for simplicity
    audio = AudioSegment.from_file(input_audio_path)
    samples = np.array(audio.get_array_of_samples())
    message_bytes = message.encode('utf-8') + b'\0'  # Null-terminated
    bits = ''.join([format(byte, '08b') for byte in message_bytes])
    if len(bits) > len(samples):
        raise ValueError("Message too long to encode in audio.")
    for i, bit in enumerate(bits):
        samples[i] = (samples[i] & ~1) | int(bit)
    encoded_audio = audio._spawn(samples.tobytes())
    encoded_audio.export(output_audio_path, format="wav")

def decode_audio(stego_audio_path: str) -> str:
    audio = AudioSegment.from_file(stego_audio_path)
    samples = np.array(audio.get_array_of_samples())
    bits = [str(samples[i] & 1) for i in range(len(samples))]
    chars = []
    for b in range(0, len(bits), 8):
        byte = bits[b:b+8]
        if len(byte) < 8:
            break
        char = int(''.join(byte), 2)
        if char == 0:
            break
        chars.append(char)
    return bytes(chars).decode('utf-8')

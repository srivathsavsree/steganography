from pydub import AudioSegment
import numpy as np
import wave
import os
import uuid
import time

def encode_audio(input_audio_path: str, message: str, output_audio_path: str) -> None:
    start_time = time.time()
    print(f"[INFO] Starting audio encoding. Input file: {input_audio_path}")
    
    try:
        # Check input file extension
        file_ext = os.path.splitext(input_audio_path.lower())[1]
        print(f"[INFO] Input file extension: {file_ext}")
        
        # Load the audio file with pydub (supports both MP3 and WAV)
        try:
            audio = AudioSegment.from_file(input_audio_path)
            print(f"[INFO] Loaded audio file. Duration: {len(audio)/1000:.2f}s, Channels: {audio.channels}, Sample width: {audio.sample_width}")
        except Exception as e:
            print(f"[ERROR] Failed to load audio file: {e}")
            raise ValueError(f"Failed to load audio file: {str(e)}. Make sure it's a valid WAV or MP3 file.")
          # For MP3 files, first convert to WAV format internally
        temp_wav_path = None
        try:
            if file_ext == '.mp3':
                print(f"[INFO] Converting MP3 to WAV format for processing")
                temp_wav_path = f"temp/{uuid.uuid4()}_temp.wav"
                audio.export(temp_wav_path, format="wav")
                audio = AudioSegment.from_wav(temp_wav_path)
                print(f"[INFO] MP3 converted to WAV format, temp file: {temp_wav_path}")
                # Now we'll use the temp_wav_path for processing
                input_audio_path = temp_wav_path
            
            # Get audio samples
            samples = np.array(audio.get_array_of_samples())
            print(f"[INFO] Extracted {len(samples)} samples from audio")
            
            message_bytes = message.encode('utf-8') + b'\0'  # Null-terminated
            bits = ''.join([format(byte, '08b') for byte in message_bytes])
            print(f"[INFO] Message converted to {len(bits)} bits")
            
            if len(bits) > len(samples):
                print(f"[ERROR] Message too long: {len(bits)} bits > {len(samples)} samples")
                raise ValueError(f"Message too long to encode in audio. Maximum size for this audio is {len(samples) // 8} bytes.")
            
            # Modify samples to encode the message
            for i, bit in enumerate(bits):
                samples[i] = (samples[i] & ~1) | int(bit)
            
            print(f"[INFO] Message encoded into audio samples")
            
            # Create new audio with modified samples
            encoded_audio = audio._spawn(samples.tobytes())
            encoded_audio.export(output_audio_path, format="wav")
            
            # Verify the output file
            if not os.path.exists(output_audio_path):
                raise ValueError(f"Failed to create output audio file: {output_audio_path}")
            
            file_size = os.path.getsize(output_audio_path)
            if file_size == 0:
                raise ValueError(f"Output audio file is empty: {output_audio_path}")
            
            print(f"[INFO] Audio encoding completed in {time.time() - start_time:.2f}s, Output size: {file_size} bytes")
        except Exception as e:
            print(f"[ERROR] Audio encoding failed during processing: {str(e)}")
            raise
        finally:
            # Clean up the temporary WAV file if it was created
            if temp_wav_path and os.path.exists(temp_wav_path):
                try:
                    os.remove(temp_wav_path)
                    print(f"[INFO] Cleaned up temporary WAV file: {temp_wav_path}")
                except Exception as cleanup_error:
                    print(f"[WARNING] Failed to clean up temporary WAV file: {cleanup_error}")
    except Exception as e:
        print(f"[ERROR] Audio encoding failed: {str(e)}")
        raise

def decode_audio(stego_audio_path: str) -> str:
    start_time = time.time()
    print(f"[INFO] Starting audio decoding. Input file: {stego_audio_path}")
    
    temp_wav_path = None
    try:
        # Check file extension
        file_ext = os.path.splitext(stego_audio_path.lower())[1]
        print(f"[INFO] Input file extension: {file_ext}")
        
        # Load the audio file (pydub supports both MP3 and WAV)
        try:
            audio = AudioSegment.from_file(stego_audio_path)
            print(f"[INFO] Loaded audio file. Duration: {len(audio)/1000:.2f}s, Channels: {audio.channels}, Sample width: {audio.sample_width}")
        except Exception as e:
            print(f"[ERROR] Failed to load audio file: {e}")
            raise ValueError(f"Failed to load audio file: {str(e)}. Make sure it's a valid WAV or MP3 file.")
        
        # For MP3 files, convert to WAV for consistent processing
        if file_ext == '.mp3':
            print(f"[INFO] Converting MP3 to WAV format for decoding")
            temp_wav_path = f"temp/{uuid.uuid4()}_temp.wav"
            audio.export(temp_wav_path, format="wav")
            audio = AudioSegment.from_wav(temp_wav_path)
            print(f"[INFO] MP3 converted to WAV format for decoding")
        
        # Get audio samples
        try:
            samples = np.array(audio.get_array_of_samples())
            print(f"[INFO] Extracted {len(samples)} samples from audio")
        except Exception as e:
            print(f"[ERROR] Failed to extract samples: {e}")
            raise ValueError(f"Failed to extract samples: {str(e)}. The audio file may be corrupted.")
        
        # Extract LSB from each sample
        bits = [str(samples[i] & 1) for i in range(len(samples))]
        
        # Convert bits to bytes and then to string
        chars = []
        for b in range(0, len(bits), 8):
            byte = bits[b:b+8]
            if len(byte) < 8:
                break
            char = int(''.join(byte), 2)
            if char == 0:  # Null terminator
                break
            chars.append(char)
        
        # Convert bytes to string
        try:
            message = bytes(chars).decode('utf-8')
            print(f"[INFO] Decoded message with length: {len(message)} characters")
            print(f"[INFO] Audio decoding completed in {time.time() - start_time:.2f}s")
            return message
        except UnicodeDecodeError as e:
            print(f"[ERROR] Failed to decode message as UTF-8: {e}")
            raise ValueError(f"Failed to decode the hidden message. The audio file may not contain a valid UTF-8 encoded message.")
    except Exception as e:
        print(f"[ERROR] Audio decoding failed: {str(e)}")
        raise
    finally:
        # Clean up temporary files
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
                print(f"[INFO] Cleaned up temporary WAV file: {temp_wav_path}")
            except Exception as cleanup_error:
                print(f"[WARNING] Failed to clean up temporary WAV file: {cleanup_error}")

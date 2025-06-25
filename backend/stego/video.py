import cv2
import numpy as np
import time
import os

def encode_video(input_path: str, message: str, output_path: str):
    # Open video file
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError("Unable to open video file")

    # Get video properties
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    codec  = cv2.VideoWriter_fourcc(*'mp4v')

    # Print video info for debugging
    print(f"[INFO] Video dimensions: {width}x{height}, FPS: {fps}, Total frames: {total_frames}")

    # Check if video is too large
    if width * height * total_frames > 50000000:  # Roughly 50MB of pixels
        print(f"[WARNING] Video is very large, processing may take a long time")
        # Consider limiting frames or resizing for large videos
        # total_frames = min(total_frames, 300)  # Limit to 300 frames if needed

    out = cv2.VideoWriter(output_path, codec, fps, (width, height))

    # Convert message to binary with delimiter
    message += "###"  # End of message delimiter
    binary_message = ''.join([format(ord(i), '08b') for i in message])
    msg_index = 0
    message_length = len(binary_message)
    
    print(f"[INFO] Message length: {len(message)} chars, Binary length: {message_length} bits")

    # Track progress and time
    start_time = time.time()
    frame_count = 0
    last_progress = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        progress = int((frame_count / total_frames) * 100)
        
        # Log progress every 10%
        if progress >= last_progress + 10:
            elapsed = time.time() - start_time
            print(f"[INFO] Encoding progress: {progress}%, Frame {frame_count}/{total_frames}, Time elapsed: {elapsed:.2f}s")
            last_progress = progress

        if msg_index < message_length:
            # Only modify enough pixels to encode the message
            pixels_needed = message_length - msg_index
            
            # Flatten the frame and modify LSBs for a portion of the frame
            flat_frame = frame.flatten()
            for i in range(min(len(flat_frame), pixels_needed)):
                if msg_index < message_length:
                    flat_frame[i] = (flat_frame[i] & ~1) | int(binary_message[msg_index])
                    msg_index += 1
                else:
                    break
            
            # Reshape frame back to original shape
            frame = flat_frame.reshape((height, width, 3))

        out.write(frame)
        
        # If message is fully encoded and we've processed at least 10% of frames, we can stop
        if msg_index >= message_length and frame_count > total_frames * 0.1:
            print(f"[INFO] Message fully encoded after {frame_count} frames, stopping early")
            # Complete the video with the remaining frames
            remaining_frames = min(int(total_frames * 0.1), 50)  # Add at least some frames
            for _ in range(remaining_frames):
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)
            break

    # Close resources
    cap.release()
    out.release()
    
    # Verify output file
    if not os.path.exists(output_path):
        raise ValueError(f"Failed to create output video file: {output_path}")
    
    file_size = os.path.getsize(output_path)
    if file_size == 0:
        raise ValueError(f"Output video file is empty: {output_path}")
    
    print(f"[INFO] Video encoding completed in {time.time() - start_time:.2f}s, Output size: {file_size} bytes")


def decode_video(input_path: str) -> str:
    start_time = time.time()
    
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError("Unable to open video file")
    
    # Get video properties for logging
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"[INFO] Decoding video: {width}x{height}, {total_frames} frames")

    binary_data = ""
    max_chars = 10000  # Reasonable limit for message length
    max_bits = max_chars * 8
    frame_count = 0
    delimiter = "###"
    decoded_message = ""
    
    # Process frames until we find the message
    while frame_count < min(300, total_frames):  # Limit to first 300 frames for efficiency
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        if frame_count % 10 == 0:
            print(f"[INFO] Decoding frame {frame_count}/{min(300, total_frames)}")
        
        # Extract bits from the first N pixels of the frame
        flat_frame = frame.flatten()
        for i in range(min(max_bits - len(binary_data), len(flat_frame))):
            binary_data += str(flat_frame[i] & 1)
            
            # Check periodically if we have enough data to extract the message
            if len(binary_data) % 8 == 0 and len(binary_data) >= 8:
                # Try to decode what we have so far
                bytes_data = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
                current_message = ""
                for byte in bytes_data:
                    if len(byte) == 8:  # Only process complete bytes
                        try:
                            char = chr(int(byte, 2))
                            current_message += char
                        except:
                            # Invalid character, might be noise
                            pass
                
                # Check if we found the delimiter
                if delimiter in current_message:
                    decoded_message = current_message.split(delimiter)[0]
                    print(f"[INFO] Found message delimiter at frame {frame_count}")
                    break
        
        # If we found the message, stop processing
        if decoded_message:
            break

    cap.release()
    
    if not decoded_message:
        # If we didn't find a complete message with delimiter, return what we have
        # Split binary to characters
        bytes_data = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
        for byte in bytes_data:
            if len(byte) == 8:
                try:
                    char = chr(int(byte, 2))
                    decoded_message += char
                except:
                    # Skip invalid characters
                    pass
    
    print(f"[INFO] Video decoding completed in {time.time() - start_time:.2f}s")
    return decoded_message

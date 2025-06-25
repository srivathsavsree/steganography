import cv2
import numpy as np

def encode_video(input_path: str, message: str, output_path: str):
    # Open video file
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError("Unable to open video file")

    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)
    codec  = cv2.VideoWriter_fourcc(*'mp4v')

    out = cv2.VideoWriter(output_path, codec, fps, (width, height))

    # Convert message to binary with delimiter
    message += "###"  # End of message delimiter
    binary_message = ''.join([format(ord(i), '08b') for i in message])
    msg_index = 0
    message_length = len(binary_message)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if msg_index < message_length:
            # Flatten the frame and modify LSBs
            flat_frame = frame.flatten()
            for i in range(len(flat_frame)):
                if msg_index < message_length:
                    flat_frame[i] = (flat_frame[i] & ~1) | int(binary_message[msg_index])
                    msg_index += 1
                else:
                    break
            # Reshape frame back to original shape
            frame = flat_frame.reshape((height, width, 3))

        out.write(frame)

    cap.release()
    out.release()


def decode_video(input_path: str) -> str:
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError("Unable to open video file")

    binary_data = ""
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        flat_frame = frame.flatten()
        for pixel in flat_frame:
            binary_data += str(pixel & 1)

    # Split binary to characters
    bytes_data = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded_message = ""
    for byte in bytes_data:
        char = chr(int(byte, 2))
        decoded_message += char
        if decoded_message.endswith("###"):
            break

    cap.release()
    return decoded_message.replace("###", "")

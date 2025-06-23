# stego/image.py
from PIL import Image
import stepic

def encode_image(input_image_path: str, message: str, output_image_path: str) -> None:
    image = Image.open(input_image_path).convert("RGB")
    encoded_image = stepic.encode(image, message.encode())
    encoded_image.save(output_image_path)

def decode_image(stego_image_path: str) -> str:
    image = Image.open(stego_image_path).convert("RGB")
    hidden_message = stepic.decode(image)
    if isinstance(hidden_message, bytes):
        return hidden_message.decode('utf-8')
    else:
        return hidden_message
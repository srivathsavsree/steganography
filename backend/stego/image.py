# stego/image.py
from PIL import Image
import stepic

def encode_image(input_image_path: str, message: str, output_image_path: str) -> None:
    image = Image.open(input_image_path).convert("RGB")
    encoded_image = stepic.encode(image, message.encode())
    encoded_image.save(output_image_path)

def decode_image(stego_image_path: str) -> str:
    try:
        print(f"[DEBUG] Opening image for decoding: {stego_image_path}")
        image = Image.open(stego_image_path).convert("RGB")
        print(f"[DEBUG] Image opened successfully, size: {image.size}, mode: {image.mode}")
        
        print("[DEBUG] Attempting to decode with stepic")
        hidden_message = stepic.decode(image)
        print(f"[DEBUG] Raw decoded message type: {type(hidden_message)}")
        
        if hidden_message is None:
            print("[WARNING] stepic.decode returned None")
            return ""
            
        if isinstance(hidden_message, bytes):
            try:
                decoded_text = hidden_message.decode('utf-8')
                print(f"[DEBUG] Successfully decoded UTF-8 message: {decoded_text[:30]}...")
                return decoded_text
            except UnicodeDecodeError as ude:
                print(f"[ERROR] UTF-8 decode error: {ude}")
                # Try another encoding or return raw bytes as string
                return str(hidden_message)
        else:
            print(f"[DEBUG] Message is already string: {hidden_message[:30]}...")
            return hidden_message
    except Exception as e:
        print(f"[ERROR] Exception in decode_image: {e}")
        raise
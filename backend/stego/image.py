# stego/image.py
from PIL import Image
import stepic
import os

def encode_image(input_image_path: str, message: str, output_image_path: str) -> None:
    try:
        print(f"[DEBUG] Opening image for encoding: {input_image_path}")
        if not os.path.exists(input_image_path):
            print(f"[ERROR] Input file does not exist: {input_image_path}")
            raise FileNotFoundError(f"Input file does not exist: {input_image_path}")
            
        file_size = os.path.getsize(input_image_path)
        print(f"[DEBUG] Input file size: {file_size} bytes")
        
        # Check if file is empty
        if file_size == 0:
            print(f"[ERROR] Input file is empty: {input_image_path}")
            raise ValueError(f"Input file is empty: {input_image_path}")
            
        # Verify image format before opening
        try:
            from PIL import UnidentifiedImageError
            image = Image.open(input_image_path)
            print(f"[DEBUG] Image format: {image.format}")
            image = image.convert("RGB")
            print(f"[DEBUG] Image opened successfully, size: {image.size}, mode: {image.mode}")
        except UnidentifiedImageError as uie:
            print(f"[ERROR] Invalid image format: {uie}")
            raise ValueError(f"Not a valid image file or format: {uie}")
        
        # Check if message is too long for the image
        max_bytes = (image.width * image.height * 3) // 8
        message_bytes = message.encode('utf-8')
        message_length = len(message_bytes)
        print(f"[DEBUG] Message length: {message_length} bytes, max capacity: {max_bytes} bytes")
        
        if message_length > max_bytes:
            print(f"[ERROR] Message too large for image: {message_length} > {max_bytes}")
            raise ValueError(f"Message is too large for this image. Max: {max_bytes} bytes, Message: {message_length} bytes")
        
        print(f"[DEBUG] Encoding message of length {len(message)} characters")
        try:
            encoded_image = stepic.encode(image, message_bytes)
            print(f"[DEBUG] Message encoded successfully")
        except Exception as stepic_error:
            print(f"[ERROR] Stepic encoding failed: {stepic_error}")
            raise ValueError(f"Stepic encoding failed: {stepic_error}")
        
        print(f"[DEBUG] Saving encoded image to {output_image_path}")
        try:
            encoded_image.save(output_image_path)
            print(f"[DEBUG] Encoded image saved successfully, size: {os.path.getsize(output_image_path)} bytes")
        except Exception as save_error:
            print(f"[ERROR] Failed to save encoded image: {save_error}")
            raise IOError(f"Failed to save encoded image: {save_error}")
        
    except Exception as e:
        print(f"[ERROR] Exception in encode_image: {e}")
        import traceback
        traceback.print_exc()
        raise

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
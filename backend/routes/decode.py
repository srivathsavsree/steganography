# routes/decode.py
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from stego.image import decode_image
import uuid
import os
import traceback
import sys

router = APIRouter()

@router.post("/image")
async def decode_image_route(image: UploadFile = File(...)):
    try:
        # Log request info
        print(f"[INFO] Decode request received for file: {image.filename}, content_type: {image.content_type}, size: {image.size}")
        
        # Validate the image
        if image.content_type != "image/png":
            print(f"[WARNING] Invalid content type: {image.content_type}")
            return JSONResponse(
                status_code=400,
                content={"detail": "Only PNG images are supported"}
            )
            
        input_path = f"temp/{uuid.uuid4()}.png"
        
        # Ensure temp directory exists
        os.makedirs("temp", exist_ok=True)
        
        try:
            # Read and save the file
            file_content = await image.read()
            print(f"[INFO] Read {len(file_content)} bytes from uploaded file")
            
            with open(input_path, "wb") as f:
                f.write(file_content)
                
            print(f"[INFO] Saved file to {input_path}, file size: {os.path.getsize(input_path)} bytes")
        except Exception as read_error:
            print(f"[ERROR] File read/write error: {read_error}")
            raise

        # Decode the message
        print(f"[INFO] Attempting to decode message from image")
        message = decode_image(input_path)
        
        if message:
            print(f"[INFO] Successfully decoded message, length: {len(message)}")
        else:
            print(f"[WARNING] Decoded message is empty")
            
        return {"message": message}
    except Exception as e:
        print(f"[ERROR] Image decoding failed: {e}")
        # Print full traceback for debugging
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        return JSONResponse(
            status_code=500,
            content={"detail": f"Decoding failed: {str(e)}"}
        )

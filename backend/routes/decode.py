# routes/decode.py
from fastapi import APIRouter, UploadFile, File
from stego.image import decode_image
import uuid
import os

router = APIRouter()

@router.post("/image")
async def decode_image_route(image: UploadFile = File(...)):
    input_path = f"temp/{uuid.uuid4()}.png"
    
    # Ensure temp directory exists
    os.makedirs("temp", exist_ok=True)
    
    with open(input_path, "wb") as f:
        f.write(await image.read())

    message = decode_image(input_path)
    return {"message": message}

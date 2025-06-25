# routes/decode.py
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from stego.image import decode_image
import uuid
import os

router = APIRouter()

@router.post("/image")
async def decode_image_route(image: UploadFile = File(...)):
    try:
        # Validate the image
        if image.content_type != "image/png":
            return JSONResponse(
                status_code=400,
                content={"detail": "Only PNG images are supported"}
            )
            
        input_path = f"temp/{uuid.uuid4()}.png"
        
        # Ensure temp directory exists
        os.makedirs("temp", exist_ok=True)
        
        with open(input_path, "wb") as f:
            f.write(await image.read())

        message = decode_image(input_path)
        return {"message": message}
    except Exception as e:
        print(f"[ERROR] Image decoding failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Decoding failed: {str(e)}"}
        )

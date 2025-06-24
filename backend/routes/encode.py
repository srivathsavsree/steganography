from fastapi import APIRouter, UploadFile, Form, File
from fastapi.responses import FileResponse
import uuid
import os
from stego.image import encode_image
from utils.s3 import upload_file_to_s3

router = APIRouter()  # ✅ THIS LINE IS REQUIRED

@router.post("/image")
async def encode_image_route(
    image: UploadFile = File(...),
    message: str = Form(...)
):
    try:
        input_path = f"temp/{uuid.uuid4()}.png"
        output_path = f"temp/{uuid.uuid4()}_encoded.png"

        os.makedirs("temp", exist_ok=True)

        with open(input_path, "wb") as f:
            f.write(await image.read())

        print(f"[INFO] Encoding message into image: {input_path}")
        encode_image(input_path, message, output_path)

        print(f"[INFO] Uploading encoded image to S3: {output_path}")
        s3_url = upload_file_to_s3(output_path)

        return {"url": s3_url}
    
    except Exception as e:
        print(f"[ERROR] Encoding failed: {e}")
        return {"error": str(e)}

# routes/encode.py
from fastapi import APIRouter, UploadFile, Form, File
from fastapi.responses import FileResponse
import uuid
import os
from stego.image import encode_image
from utils.s3 import upload_file_to_s3

router = APIRouter()

@router.post("/image")
async def encode_image_route(
    image: UploadFile = File(...),
    message: str = Form(...)
):
    input_path = f"temp/{uuid.uuid4()}.png"
    output_path = f"temp/{uuid.uuid4()}_encoded.png"

    # Ensure temp directory exists
    os.makedirs("temp", exist_ok=True)

    with open(input_path, "wb") as f:
        f.write(await image.read())

    encode_image(input_path, message, output_path)

    # Upload to S3 and return the public URL
    s3_url = upload_file_to_s3(output_path)
    return {"url": s3_url}

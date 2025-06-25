# routes/file.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import uuid
import os
import mimetypes
from stego.image_file import encode_image_with_file, decode_file_from_image
from utils.s3 import upload_file_to_s3

router = APIRouter()

@router.post("/encode")
async def encode_image_file_route(
    image: UploadFile = File(...),
    file: UploadFile = File(...)
):
    os.makedirs("temp", exist_ok=True)

    if image.content_type != "image/png":
        raise HTTPException(status_code=400, detail="Only PNG images supported.")

    input_image_path = f"temp/{uuid.uuid4()}.png"
    input_file_path = f"temp/{uuid.uuid4()}_{file.filename}"
    output_path = f"temp/{uuid.uuid4()}_encoded.png"

    try:
        print(f"[INFO] Saving input files to temp directory")
        with open(input_image_path, "wb") as f_img:
            f_img.write(await image.read())
        with open(input_file_path, "wb") as f_file:
            f_file.write(await file.read())

        print(f"[INFO] Encoding file into image")
        encode_image_with_file(input_image_path, input_file_path, output_path)

        print(f"[INFO] Uploading encoded image to S3")
        s3_url = upload_file_to_s3(output_path)

        return {"url": s3_url}

    except Exception as e:
        print(f"[ERROR] Encoding failed: {e}")
        raise HTTPException(status_code=500, detail=f"Encoding failed: {str(e)}")


@router.post("/decode")
async def decode_image_file_route(
    image: UploadFile = File(...)
):
    os.makedirs("temp", exist_ok=True)

    if image.content_type != "image/png":
        raise HTTPException(status_code=400, detail="Only PNG images supported.")

    input_image_path = f"temp/{uuid.uuid4()}.png"

    try:
        print(f"[INFO] Saving uploaded encoded image to: {input_image_path}")
        with open(input_image_path, "wb") as f_img:
            f_img.write(await image.read())

        print(f"[INFO] Decoding file from image")
        output_path = decode_file_from_image(input_image_path, "temp")

        filename = os.path.basename(output_path)
        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        print(f"[INFO] Returning extracted file: {filename}")
        return FileResponse(output_path, media_type=mime_type, filename=filename)

    except Exception as e:
        print(f"[ERROR] Decoding failed: {e}")
        raise HTTPException(status_code=500, detail=f"Decoding failed: {str(e)}")

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import uuid
import os
import mimetypes
from utils.s3 import upload_file_to_s3
from stego.video import encode_video, decode_video

router = APIRouter()

@router.post("/encode")
async def encode_video_route(
    video: UploadFile = File(...),
    message: str = File(...)
):
    os.makedirs("temp", exist_ok=True)

    input_ext = os.path.splitext(video.filename)[1] or ".mp4"
    input_path = f"temp/{uuid.uuid4()}{input_ext}"
    output_path = f"temp/{uuid.uuid4()}_encoded{input_ext}"

    try:
        with open(input_path, "wb") as f:
            f.write(await video.read())

        encode_video(input_path, message, output_path)

        s3_url = upload_file_to_s3(output_path)
        return {"url": s3_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encoding failed: {str(e)}")

@router.post("/decode")
async def decode_video_route(
    video: UploadFile = File(...)
):
    os.makedirs("temp", exist_ok=True)

    input_ext = os.path.splitext(video.filename)[1] or ".mp4"
    input_path = f"temp/{uuid.uuid4()}{input_ext}"

    try:
        with open(input_path, "wb") as f:
            f.write(await video.read())

        message = decode_video(input_path)
        return {"message": message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decoding failed: {str(e)}")

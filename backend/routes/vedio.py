from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import uuid
import os
from utils.s3 import upload_file_to_s3
from stego.video import encode_video, decode_video

router = APIRouter()

@router.post("/encode")
async def encode_video_route(
    video: UploadFile = File(...),
    message: str = Form(...)  # Accepting text input from form
):
    os.makedirs("temp", exist_ok=True)

    input_ext = os.path.splitext(video.filename)[1] or ".mp4"
    input_path = f"temp/{uuid.uuid4()}{input_ext}"
    output_path = f"temp/{uuid.uuid4()}_encoded{input_ext}"

    try:
        # Save uploaded video to disk
        with open(input_path, "wb") as f:
            f.write(await video.read())

        # Call your encoding function
        encode_video(input_path, message, output_path)

        # Upload encoded video to S3 and return the link
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
        # Save uploaded video to disk
        with open(input_path, "wb") as f:
            f.write(await video.read())

        # Decode the hidden message from the video
        message = decode_video(input_path)
        return {"message": message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decoding failed: {str(e)}")

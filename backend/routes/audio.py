# routes/audio.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import uuid
import os
from stego.audio import encode_audio, decode_audio
from utils.s3 import upload_file_to_s3

router = APIRouter()

@router.post("/encode")
async def encode_audio_route(
    audio: UploadFile = File(...),
    message: str = Form(...)
):
    if audio.content_type not in ["audio/wav", "audio/x-wav", "audio/mp3"]:
        raise HTTPException(status_code=400, detail="Only WAV or MP3 files are supported.")

    os.makedirs("temp", exist_ok=True)

    input_ext = ".wav" if "wav" in audio.content_type else ".mp3"
    input_path = f"temp/{uuid.uuid4()}{input_ext}"
    output_path = f"temp/{uuid.uuid4()}_encoded.wav"

    try:
        print(f"[INFO] Saving uploaded audio to {input_path}")
        with open(input_path, "wb") as f:
            f.write(await audio.read())

        print(f"[INFO] Encoding message into audio")
        encode_audio(input_path, message, output_path)

        print(f"[INFO] Uploading encoded audio to S3")
        s3_url = upload_file_to_s3(output_path)

        return {"url": s3_url}

    except Exception as e:
        print(f"[ERROR] Audio encoding failed: {e}")
        raise HTTPException(status_code=500, detail=f"Encoding failed: {str(e)}")


@router.post("/decode")
async def decode_audio_route(
    audio: UploadFile = File(...)
):
    if audio.content_type not in ["audio/wav", "audio/x-wav", "audio/mp3"]:
        raise HTTPException(status_code=400, detail="Only WAV or MP3 files are supported.")

    os.makedirs("temp", exist_ok=True)

    input_ext = ".wav" if "wav" in audio.content_type else ".mp3"
    input_path = f"temp/{uuid.uuid4()}{input_ext}"

    try:
        print(f"[INFO] Saving uploaded audio to {input_path}")
        with open(input_path, "wb") as f:
            f.write(await audio.read())

        print(f"[INFO] Decoding message from audio")
        message = decode_audio(input_path)

        return JSONResponse({"message": message})

    except Exception as e:
        print(f"[ERROR] Audio decoding failed: {e}")
        raise HTTPException(status_code=500, detail=f"Decoding failed: {str(e)}")
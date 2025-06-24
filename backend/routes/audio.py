from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import uuid
import os
from stego.audio import encode_audio, decode_audio

router = APIRouter()

@router.post("/encode")
async def encode_audio_route(
    audio: UploadFile = File(...),
    message: str = Form(...)
):
    if audio.content_type not in ["audio/wav", "audio/x-wav", "audio/mp3"]:
        raise HTTPException(status_code=400, detail="Only WAV or MP3 files are supported.")
    input_ext = ".wav" if "wav" in audio.content_type else ".mp3"
    input_path = f"temp/{uuid.uuid4()}{input_ext}"
    output_path = f"temp/{uuid.uuid4()}_encoded.wav"
    
    with open(input_path, "wb") as f:
        f.write(await audio.read())
        
    try:
        encode_audio(input_path, message, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encoding failed: {str(e)}")
    
    return FileResponse(output_path, media_type="audio/wav", filename="encoded.wav")

@router.post("/decode")
async def decode_audio_route(
    audio: UploadFile = File(...)
):
    if audio.content_type not in ["audio/wav", "audio/x-wav", "audio/mp3"]:
        raise HTTPException(status_code=400, detail="Only WAV or MP3 files are supported.")
    input_ext = ".wav" if "wav" in audio.content_type else ".mp3"
    input_path = f"temp/{uuid.uuid4()}{input_ext}"
    
    with open(input_path, "wb") as f:
        f.write(await audio.read())
        
    try:
        message = decode_audio(input_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decoding failed: {str(e)}")
        
    return JSONResponse({"message": message})

from fastapi import APIRouter
import os

router = APIRouter()

@router.post("/encode")
async def encode_video_route():
    # Ensure temp directory exists
    os.makedirs("temp", exist_ok=True)
    return {"message": "Video steganography encode coming soon."}

@router.post("/decode")
async def decode_video_route():
    # Ensure temp directory exists
    os.makedirs("temp", exist_ok=True)
    return {"message": "Video steganography decode coming soon."}

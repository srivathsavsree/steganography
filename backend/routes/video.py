from fastapi import APIRouter

router = APIRouter()

@router.post("/encode/video")
async def encode_video_route():
    return {"message": "Video steganography encode coming soon."}

@router.post("/decode/video")
async def decode_video_route():
    return {"message": "Video steganography decode coming soon."}

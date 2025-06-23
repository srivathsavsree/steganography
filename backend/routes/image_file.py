from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import uuid
import os
from stego.image_file import encode_image_with_file, decode_file_from_image

router = APIRouter()

@router.post("/encode/image-file")
async def encode_image_file_route(
    image: UploadFile = File(...),
    file: UploadFile = File(...)
):
    if image.content_type != "image/png":
        raise HTTPException(status_code=400, detail="Only PNG images supported.")
    input_image_path = f"temp/{uuid.uuid4()}.png"
    input_file_path = f"temp/{uuid.uuid4()}_{file.filename}"
    output_path = f"temp/{uuid.uuid4()}_encoded.png"
    with open(input_image_path, "wb") as f_img:
        f_img.write(await image.read())
    with open(input_file_path, "wb") as f_file:
        f_file.write(await file.read())
    try:
        encode_image_with_file(input_image_path, input_file_path, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encoding failed: {str(e)}")
    return FileResponse(output_path, media_type="image/png", filename="encoded_with_file.png")

@router.post("/decode/image-file")
async def decode_image_file_route(
    image: UploadFile = File(...)
):
    if image.content_type != "image/png":
        raise HTTPException(status_code=400, detail="Only PNG images supported.")
    input_image_path = f"temp/{uuid.uuid4()}.png"
    with open(input_image_path, "wb") as f_img:
        f_img.write(await image.read())
    try:
        output_path = decode_file_from_image(input_image_path, "temp")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decoding failed: {str(e)}")
    filename = os.path.basename(output_path)
    mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    return FileResponse(output_path, media_type=mime_type, filename=filename)

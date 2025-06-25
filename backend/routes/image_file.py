# routes/image_file.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import uuid
import os
import mimetypes
import traceback
from stego.image_file import encode_image_with_file, decode_file_from_image
from utils.s3 import upload_file_to_s3

router = APIRouter()

@router.post("/encode")
async def encode_image_file_route(
    image: UploadFile = File(...),
    file: UploadFile = File(...)
):
    try:
        # Log request info
        print(f"[INFO] Encode file-in-image request received")
        print(f"[INFO] Image: {image.filename}, content_type: {image.content_type}")
        print(f"[INFO] File: {file.filename}, content_type: {file.content_type}, size: {file.size}")
        
        os.makedirs("temp", exist_ok=True)

        # Check if temp directory is writable
        try:
            test_file = f"temp/test_{uuid.uuid4()}.txt"
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            print(f"[INFO] Temp directory is writable")
        except Exception as perm_error:
            print(f"[ERROR] Temp directory permission error: {perm_error}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Server configuration error: Unable to write to temp directory"}
            )

        if image.content_type != "image/png":
            print(f"[WARNING] Invalid image content type: {image.content_type}")
            return JSONResponse(
                status_code=400,
                content={"detail": "Only PNG images supported."}
            )

        input_image_path = f"temp/{uuid.uuid4()}.png"
        input_file_path = f"temp/{uuid.uuid4()}_{file.filename}"
        output_path = f"temp/{uuid.uuid4()}_encoded.png"

        try:
            # Read and save the files
            image_content = await image.read()
            file_content = await file.read()
            
            print(f"[INFO] Read {len(image_content)} bytes from uploaded image")
            print(f"[INFO] Read {len(file_content)} bytes from uploaded file")
            
            with open(input_image_path, "wb") as f_img:
                f_img.write(image_content)
            with open(input_file_path, "wb") as f_file:
                f_file.write(file_content)
                
            print(f"[INFO] Saved image to {input_image_path}, file size: {os.path.getsize(input_image_path)} bytes")
            print(f"[INFO] Saved file to {input_file_path}, file size: {os.path.getsize(input_file_path)} bytes")
        except Exception as read_error:
            print(f"[ERROR] File read/write error: {read_error}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error reading or writing files: {str(read_error)}"}
            )

        try:
            print(f"[INFO] Encoding file into image")
            encode_image_with_file(input_image_path, input_file_path, output_path)
            print(f"[INFO] Successfully encoded file, output size: {os.path.getsize(output_path)} bytes")
        except Exception as encode_error:
            print(f"[ERROR] Encoding algorithm failed: {encode_error}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error in encoding algorithm: {str(encode_error)}"}
            )

        try:
            print(f"[INFO] Uploading encoded image to S3: {output_path}")
            
            # Check if the output file exists
            if not os.path.exists(output_path):
                print(f"[ERROR] Output file does not exist: {output_path}")
                return JSONResponse(
                    status_code=500,
                    content={"detail": f"Encoded output file does not exist: {output_path}"}
                )
                
            # Check if the output file is empty
            if os.path.getsize(output_path) == 0:
                print(f"[ERROR] Output file is empty: {output_path}")
                return JSONResponse(
                    status_code=500,
                    content={"detail": f"Encoded output file is empty: {output_path}"}
                )
                
            # Upload to S3
            try:
                s3_url = upload_file_to_s3(output_path)
                print(f"[INFO] Successfully uploaded to S3, URL: {s3_url}")
                return {"url": s3_url}
            except Exception as s3_error:
                print(f"[ERROR] S3 upload failed: {s3_error}")
                print(f"[ERROR] Error type: {type(s3_error)}")
                traceback.print_exc()
                
                # As a fallback, try to serve the file directly
                print(f"[INFO] Trying to serve the file directly")
                return FileResponse(
                    output_path,
                    media_type="image/png",
                    filename="encoded.png"
                )
        except Exception as s3_error:
            print(f"[ERROR] S3 upload failed: {s3_error}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error uploading to S3: {str(s3_error)}"}
            )
            
    except Exception as e:
        print(f"[ERROR] Unexpected error in encode file-in-image route: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Encoding failed: {str(e)}"}
        )


@router.post("/decode")
async def decode_image_file_route(
    image: UploadFile = File(...)
):
    try:
        # Log request info
        print(f"[INFO] Decode file-from-image request received")
        print(f"[INFO] Image: {image.filename}, content_type: {image.content_type}")
        
        os.makedirs("temp", exist_ok=True)

        if image.content_type != "image/png":
            print(f"[WARNING] Invalid image content type: {image.content_type}")
            return JSONResponse(
                status_code=400,
                content={"detail": "Only PNG images supported."}
            )

        input_image_path = f"temp/{uuid.uuid4()}.png"

        try:
            # Read and save the image file
            image_content = await image.read()
            print(f"[INFO] Read {len(image_content)} bytes from uploaded image")
            
            with open(input_image_path, "wb") as f_img:
                f_img.write(image_content)
                
            print(f"[INFO] Saved image to {input_image_path}, file size: {os.path.getsize(input_image_path)} bytes")
        except Exception as read_error:
            print(f"[ERROR] File read/write error: {read_error}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error reading or writing image file: {str(read_error)}"}
            )

        try:
            print(f"[INFO] Decoding file from image: {input_image_path}")
            output_path = decode_file_from_image(input_image_path, "temp")
            
            if not os.path.exists(output_path):
                print(f"[ERROR] Extracted file does not exist: {output_path}")
                return JSONResponse(
                    status_code=500, 
                    content={"detail": "Failed to extract file from image."}
                )
                
            print(f"[INFO] Successfully extracted file: {output_path}, size: {os.path.getsize(output_path)} bytes")

            filename = os.path.basename(output_path)
            mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

            print(f"[INFO] Returning extracted file: {filename}, mime type: {mime_type}")
            return FileResponse(output_path, media_type=mime_type, filename=filename)
        except Exception as decode_error:
            print(f"[ERROR] Decoding algorithm failed: {decode_error}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error in decoding algorithm: {str(decode_error)}"}
            )
    except Exception as e:
        print(f"[ERROR] Unexpected error in decode file-from-image route: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Decoding failed: {str(e)}"}
        )


@router.post("/encode/direct")
async def encode_image_file_direct(
    image: UploadFile = File(...),
    file: UploadFile = File(...)
):
    """
    Encode a file in an image and serve it directly without S3 upload.
    This endpoint is a fallback for when S3 is not available.
    """
    try:
        # Log request info
        print(f"[INFO] Direct encode file-in-image request received")
        print(f"[INFO] Image: {image.filename}, content_type: {image.content_type}")
        print(f"[INFO] File: {file.filename}, content_type: {file.content_type}, size: {file.size}")
        
        os.makedirs("temp", exist_ok=True)

        if image.content_type != "image/png":
            print(f"[WARNING] Invalid image content type: {image.content_type}")
            return JSONResponse(
                status_code=400,
                content={"detail": "Only PNG images supported."}
            )

        input_image_path = f"temp/{uuid.uuid4()}.png"
        input_file_path = f"temp/{uuid.uuid4()}_{file.filename}"
        output_path = f"temp/{uuid.uuid4()}_encoded.png"

        # Read and save the files
        image_content = await image.read()
        file_content = await file.read()
        
        with open(input_image_path, "wb") as f_img:
            f_img.write(image_content)
        with open(input_file_path, "wb") as f_file:
            f_file.write(file_content)
            
        print(f"[INFO] Saved image to {input_image_path}, file size: {os.path.getsize(input_image_path)} bytes")
        print(f"[INFO] Saved file to {input_file_path}, file size: {os.path.getsize(input_file_path)} bytes")

        # Encode file into image
        print(f"[INFO] Encoding file into image")
        encode_image_with_file(input_image_path, input_file_path, output_path)
        print(f"[INFO] Successfully encoded file, output size: {os.path.getsize(output_path)} bytes")

        # Return the file directly
        return FileResponse(
            output_path,
            media_type="image/png",
            filename="encoded.png"
        )
            
    except Exception as e:
        print(f"[ERROR] Unexpected error in direct encode file-in-image route: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Direct encoding failed: {str(e)}"}
        )

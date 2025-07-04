from fastapi import APIRouter, UploadFile, Form, File
from fastapi.responses import FileResponse, JSONResponse
import uuid
import os
from stego.image import encode_image
from utils.s3 import upload_file_to_s3

router = APIRouter()  # ✅ THIS LINE IS REQUIRED

@router.post("/image")
async def encode_image_route(
    image: UploadFile = File(...),
    message: str = Form(...)
):
    try:
        # Log request info
        print(f"[INFO] Encode request received for file: {image.filename}, content_type: {image.content_type}, size: {image.size}")
        print(f"[INFO] Message length: {len(message)}")
        
        # Validate the image
        if image.content_type != "image/png":
            print(f"[WARNING] Invalid content type: {image.content_type}")
            return JSONResponse(
                status_code=400,
                content={"detail": f"Only PNG images are supported, received {image.content_type}"}
            )
            
        input_path = f"temp/{uuid.uuid4()}.png"
        output_path = f"temp/{uuid.uuid4()}_encoded.png"

        # Ensure temp directory exists
        os.makedirs("temp", exist_ok=True)

        try:
            # Read and save the file
            file_content = await image.read()
            print(f"[INFO] Read {len(file_content)} bytes from uploaded file")
            
            with open(input_path, "wb") as f:
                f.write(file_content)
                
            print(f"[INFO] Saved file to {input_path}, file size: {os.path.getsize(input_path)} bytes")
        except Exception as read_error:
            print(f"[ERROR] File read/write error: {read_error}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error reading or writing image file: {str(read_error)}"}
            )

        try:
            print(f"[INFO] Encoding message into image: {input_path}")
            encode_image(input_path, message, output_path)
            print(f"[INFO] Successfully encoded message, output file size: {os.path.getsize(output_path)} bytes")
        except Exception as encode_error:
            print(f"[ERROR] Encoding algorithm failed: {encode_error}")
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
                import traceback
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
        print(f"[ERROR] Unexpected error in encode route: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Encoding failed: {str(e)}"}
        )

@router.post("/image/direct")
async def encode_image_direct(
    image: UploadFile = File(...),
    message: str = Form(...)
):
    """
    Encode an image and serve it directly without S3 upload.
    This endpoint is a fallback for when S3 is not available.
    """
    try:
        # Log request info
        print(f"[INFO] Direct encode request received for file: {image.filename}, content_type: {image.content_type}, size: {image.size}")
        print(f"[INFO] Message length: {len(message)}")
        
        # Validate the image
        if image.content_type != "image/png":
            print(f"[WARNING] Invalid content type: {image.content_type}")
            return JSONResponse(
                status_code=400,
                content={"detail": f"Only PNG images are supported, received {image.content_type}"}
            )
            
        input_path = f"temp/{uuid.uuid4()}.png"
        output_path = f"temp/{uuid.uuid4()}_encoded.png"

        # Ensure temp directory exists
        os.makedirs("temp", exist_ok=True)

        # Read and save the file
        file_content = await image.read()
        print(f"[INFO] Read {len(file_content)} bytes from uploaded file")
        
        with open(input_path, "wb") as f:
            f.write(file_content)
            
        print(f"[INFO] Saved file to {input_path}, file size: {os.path.getsize(input_path)} bytes")

        # Encode the message
        print(f"[INFO] Encoding message into image: {input_path}")
        encode_image(input_path, message, output_path)
        print(f"[INFO] Successfully encoded message, output file size: {os.path.getsize(output_path)} bytes")

        # Return the file directly
        return FileResponse(
            output_path,
            media_type="image/png",
            filename="encoded.png"
        )
            
    except Exception as e:
        print(f"[ERROR] Unexpected error in direct encode route: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Direct encoding failed: {str(e)}"}
        )

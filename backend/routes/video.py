from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
import uuid
import os
import traceback
from utils.s3 import upload_file_to_s3
from stego.video import encode_video, decode_video

router = APIRouter()

@router.post("/encode")
async def encode_video_route(
    video: UploadFile = File(...),
    message: str = Form(...)
):
    try:
        # Log request info
        print(f"[INFO] Encode video request received for file: {video.filename}, content_type: {video.content_type}")
        print(f"[INFO] Message length: {len(message)}")
        
        os.makedirs("temp", exist_ok=True)

        # Validate video content type and file extension
        valid_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        file_ext = os.path.splitext(video.filename.lower())[1]
        
        # More permissive content type check
        is_valid_content_type = (
            video.content_type.startswith("video/") or 
            "video" in video.content_type.lower() or
            file_ext in valid_extensions
        )
        
        if not is_valid_content_type:
            print(f"[WARNING] Invalid content type: {video.content_type}, file extension: {file_ext}")
            return JSONResponse(
                status_code=400,
                content={"detail": f"Only video files are supported. Supported formats: MP4, AVI, MOV, MKV. Received content type: {video.content_type}, file extension: {file_ext}"}
            )
            
        # Check message length
        if len(message) > 10000:
            print(f"[WARNING] Message too long: {len(message)} characters")
            return JSONResponse(
                status_code=400,
                content={"detail": f"Message too long. Maximum length is 10000 characters."}
            )

        input_ext = os.path.splitext(video.filename)[1] or ".mp4"
        input_path = f"temp/{uuid.uuid4()}{input_ext}"
        output_path = f"temp/{uuid.uuid4()}_encoded{input_ext}"

        try:
            # Read and save the file
            file_content = await video.read()
            print(f"[INFO] Read {len(file_content)} bytes from uploaded video")
            
            # Check file size
            if len(file_content) > 50 * 1024 * 1024:  # 50 MB limit
                print(f"[WARNING] File too large: {len(file_content)} bytes")
                return JSONResponse(
                    status_code=400,
                    content={"detail": f"File too large. Maximum size is 50 MB."}
                )
            
            with open(input_path, "wb") as f:
                f.write(file_content)
                
            print(f"[INFO] Saved video to {input_path}, file size: {os.path.getsize(input_path)} bytes")
        except Exception as read_error:
            print(f"[ERROR] File read/write error: {read_error}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error reading or writing video file: {str(read_error)}"}
            )

        try:
            print(f"[INFO] Encoding message into video: {input_path}")
            print(f"[INFO] Video file size: {os.path.getsize(input_path)} bytes")
            print(f"[INFO] Video content type: {video.content_type}")
            print(f"[INFO] Message length: {len(message)} characters")
            
            # Check if file exists and is readable
            if not os.path.exists(input_path):
                print(f"[ERROR] Input file does not exist: {input_path}")
                return JSONResponse(
                    status_code=500,
                    content={"detail": "Internal error: Could not save uploaded file"}
                )
                
            # Check if the file is readable
            try:
                with open(input_path, 'rb') as f:
                    test = f.read(1024)  # Try reading some bytes
                print(f"[INFO] Input file is readable")
            except Exception as io_error:
                print(f"[ERROR] Input file is not readable: {io_error}")
                return JSONResponse(
                    status_code=500,
                    content={"detail": "Internal error: Could not read uploaded file"}
                )
            
            # Encode the video
            encode_video(input_path, message, output_path)
            print(f"[INFO] Successfully encoded message, output file size: {os.path.getsize(output_path)} bytes")
        except Exception as encode_error:
            print(f"[ERROR] Encoding algorithm failed: {encode_error}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error in encoding algorithm: {str(encode_error)}"}
            )

        try:
            print(f"[INFO] Uploading encoded video to S3: {output_path}")
            
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
                    media_type=f"video/{input_ext.lstrip('.')}",
                    filename=f"encoded{input_ext}"
                )
        except Exception as s3_error:
            print(f"[ERROR] S3 upload failed: {s3_error}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error uploading to S3: {str(s3_error)}"}
            )
            
    except Exception as e:
        print(f"[ERROR] Unexpected error in encode video route: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Encoding failed: {str(e)}"}
        )

@router.post("/decode")
async def decode_video_route(
    video: UploadFile = File(...)
):
    try:
        # Log request info
        print(f"[INFO] Decode video request received for file: {video.filename}, content_type: {video.content_type}")
        
        os.makedirs("temp", exist_ok=True)

        # Validate video content type and file extension
        valid_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        file_ext = os.path.splitext(video.filename.lower())[1]
        
        # More permissive content type check
        is_valid_content_type = (
            video.content_type.startswith("video/") or 
            "video" in video.content_type.lower() or
            file_ext in valid_extensions
        )
        
        if not is_valid_content_type:
            print(f"[WARNING] Invalid content type: {video.content_type}, file extension: {file_ext}")
            return JSONResponse(
                status_code=400,
                content={"detail": f"Only video files are supported. Supported formats: MP4, AVI, MOV, MKV. Received content type: {video.content_type}, file extension: {file_ext}"}
            )

        input_ext = os.path.splitext(video.filename)[1] or ".mp4"
        input_path = f"temp/{uuid.uuid4()}{input_ext}"

        try:
            # Read and save the file
            file_content = await video.read()
            print(f"[INFO] Read {len(file_content)} bytes from uploaded video")
            
            with open(input_path, "wb") as f:
                f.write(file_content)
                
            print(f"[INFO] Saved video to {input_path}, file size: {os.path.getsize(input_path)} bytes")
        except Exception as read_error:
            print(f"[ERROR] File read/write error: {read_error}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error reading or writing video file: {str(read_error)}"}
            )

        try:
            print(f"[INFO] Decoding message from video: {input_path}")
            message = decode_video(input_path)
            print(f"[INFO] Successfully decoded message from video")
            return JSONResponse({"message": message})
        except Exception as decode_error:
            print(f"[ERROR] Decoding algorithm failed: {decode_error}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error in decoding algorithm: {str(decode_error)}"}
            )
    except Exception as e:
        print(f"[ERROR] Unexpected error in decode video route: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Decoding failed: {str(e)}"}
        )

@router.post("/encode/direct")
async def encode_video_direct(
    video: UploadFile = File(...),
    message: str = Form(...)
):
    """
    Encode a video and serve it directly without S3 upload.
    This endpoint is a fallback for when S3 is not available.
    """
    try:
        # Log request info
        print(f"[INFO] Direct encode video request received for file: {video.filename}, content_type: {video.content_type}")
        print(f"[INFO] Message length: {len(message)}")
        
        os.makedirs("temp", exist_ok=True)

        # Validate video content type and file extension
        valid_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        file_ext = os.path.splitext(video.filename.lower())[1]
        
        # More permissive content type check
        is_valid_content_type = (
            video.content_type.startswith("video/") or 
            "video" in video.content_type.lower() or
            file_ext in valid_extensions
        )
        
        if not is_valid_content_type:
            print(f"[WARNING] Invalid content type: {video.content_type}, file extension: {file_ext}")
            return JSONResponse(
                status_code=400,
                content={"detail": f"Only video files are supported. Supported formats: MP4, AVI, MOV, MKV. Received content type: {video.content_type}, file extension: {file_ext}"}
            )

        input_ext = os.path.splitext(video.filename)[1] or ".mp4"
        input_path = f"temp/{uuid.uuid4()}{input_ext}"
        output_path = f"temp/{uuid.uuid4()}_encoded{input_ext}"

        # Read and save the file
        file_content = await video.read()
        print(f"[INFO] Read {len(file_content)} bytes from uploaded video")
        
        with open(input_path, "wb") as f:
            f.write(file_content)
            
        print(f"[INFO] Saved video to {input_path}, file size: {os.path.getsize(input_path)} bytes")

        # Encode the message
        print(f"[INFO] Encoding message into video: {input_path}")
        encode_video(input_path, message, output_path)
        print(f"[INFO] Successfully encoded message, output file size: {os.path.getsize(output_path)} bytes")

        # Return the file directly
        return FileResponse(
            output_path,
            media_type=f"video/{input_ext.lstrip('.')}",
            filename=f"encoded{input_ext}"
        )
            
    except Exception as e:
        print(f"[ERROR] Unexpected error in direct encode video route: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Direct encoding failed: {str(e)}"}
        )

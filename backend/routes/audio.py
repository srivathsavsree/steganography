# routes/audio.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import uuid
import os
import traceback
from stego.audio import encode_audio, decode_audio
from utils.s3 import upload_file_to_s3

router = APIRouter()

@router.post("/encode")
async def encode_audio_route(
    audio: UploadFile = File(...),
    message: str = Form(...)
):
    try:
        # Log request info
        print(f"[INFO] Encode audio request received for file: {audio.filename}, content_type: {audio.content_type}")
        print(f"[INFO] Message length: {len(message)}")
        
        # Validate the audio file
        print(f"[INFO] Audio content type: {audio.content_type}, filename: {audio.filename}")
        
        # Check file extension and content type
        valid_extensions = ['.wav', '.mp3']
        file_ext = os.path.splitext(audio.filename.lower())[1]
        
        # More permissive content type check
        is_valid_content_type = (
            audio.content_type.startswith("audio/") or 
            "audio" in audio.content_type.lower() or
            file_ext in valid_extensions
        )
        
        if not is_valid_content_type or file_ext not in valid_extensions:
            print(f"[WARNING] Invalid content type or file extension: {audio.content_type}, {file_ext}")
            return JSONResponse(
                status_code=400, 
                content={"detail": f"Only WAV or MP3 files are supported. Please upload a file with .wav or .mp3 extension. You uploaded a file with content type: {audio.content_type} and extension: {file_ext}"}
            )
            
        # Check message length
        if len(message) > 10000:
            print(f"[WARNING] Message too long: {len(message)} characters")
            return JSONResponse(
                status_code=400,
                content={"detail": f"Message too long. Maximum length is 10000 characters."}
            )

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

        # Get file extension from the uploaded file
        file_ext = os.path.splitext(audio.filename.lower())[1]
        if not file_ext:
            file_ext = ".wav"  # Default to .wav if no extension
            
        # Generate unique paths with proper extensions
        input_path = f"temp/{uuid.uuid4()}{file_ext}"
        output_path = f"temp/{uuid.uuid4()}_encoded.wav"  # Output is always WAV

        try:
            # Read and save the file
            file_content = await audio.read()
            print(f"[INFO] Read {len(file_content)} bytes from uploaded audio file")
            
            # Check file size
            if len(file_content) > 25 * 1024 * 1024:  # 25 MB limit
                print(f"[WARNING] File too large: {len(file_content)} bytes")
                return JSONResponse(
                    status_code=400,
                    content={"detail": f"File too large. Maximum size is 25 MB."}
                )
            
            with open(input_path, "wb") as f:
                f.write(file_content)
                
            print(f"[INFO] Saved audio to {input_path}, file size: {os.path.getsize(input_path)} bytes")
        except Exception as read_error:
            print(f"[ERROR] File read/write error: {read_error}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error reading or writing audio file: {str(read_error)}"}
            )

        try:
            print(f"[INFO] Encoding message into audio: {input_path}")
            
            # Make sure the file exists before trying to encode
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
            
            # Proceed with encoding
            try:
                encode_audio(input_path, message, output_path)
                print(f"[INFO] Successfully encoded message, output file size: {os.path.getsize(output_path)} bytes")
            except ValueError as value_error:
                print(f"[ERROR] Encoding value error: {value_error}")
                return JSONResponse(
                    status_code=400,
                    content={"detail": str(value_error)}
                )
                
        except Exception as encode_error:
            print(f"[ERROR] Encoding algorithm failed: {encode_error}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error in encoding algorithm: {str(encode_error)}"}
            )

        try:
            print(f"[INFO] Uploading encoded audio to S3: {output_path}")
            
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
                print(f"[INFO] Trying to serve the audio file directly")
                return FileResponse(
                    output_path,
                    media_type="audio/wav",
                    filename="encoded.wav"
                )
        except Exception as s3_error:
            print(f"[ERROR] S3 upload failed: {s3_error}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error uploading to S3: {str(s3_error)}"}
            )
            
    except Exception as e:
        print(f"[ERROR] Unexpected error in encode audio route: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Encoding failed: {str(e)}"}
        )


@router.post("/decode")
async def decode_audio_route(
    audio: UploadFile = File(...)
):
    try:
        # Log request info
        print(f"[INFO] Decode audio request received for file: {audio.filename}, content_type: {audio.content_type}")
        
        # Check file extension and content type
        valid_extensions = ['.wav', '.mp3']
        file_ext = os.path.splitext(audio.filename.lower())[1]
        
        # More permissive content type check
        is_valid_content_type = (
            audio.content_type.startswith("audio/") or 
            "audio" in audio.content_type.lower() or
            file_ext in valid_extensions
        )
        
        if not is_valid_content_type or file_ext not in valid_extensions:
            print(f"[WARNING] Invalid content type or file extension: {audio.content_type}, {file_ext}")
            return JSONResponse(
                status_code=400, 
                content={"detail": f"Only WAV or MP3 files are supported. Please upload a file with .wav or .mp3 extension. You uploaded a file with content type: {audio.content_type} and extension: {file_ext}"}
            )

        os.makedirs("temp", exist_ok=True)

        # Get file extension from the uploaded file
        file_ext = os.path.splitext(audio.filename.lower())[1]
        if not file_ext:
            file_ext = ".wav"  # Default to .wav if no extension
            
        # Generate unique path with proper extension
        input_path = f"temp/{uuid.uuid4()}{file_ext}"
        
        print(f"[INFO] Using file extension: {file_ext}, input path: {input_path}")

        try:
            # Read and save the file
            file_content = await audio.read()
            print(f"[INFO] Read {len(file_content)} bytes from uploaded audio file")
            
            with open(input_path, "wb") as f:
                f.write(file_content)
                
            print(f"[INFO] Saved audio to {input_path}, file size: {os.path.getsize(input_path)} bytes")
        except Exception as read_error:
            print(f"[ERROR] File read/write error: {read_error}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error reading or writing audio file: {str(read_error)}"}
            )

        try:
            print(f"[INFO] Decoding message from audio: {input_path}")
            message = decode_audio(input_path)
            print(f"[INFO] Successfully decoded message from audio")
            return JSONResponse({"message": message})
        except Exception as decode_error:
            print(f"[ERROR] Decoding algorithm failed: {decode_error}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error in decoding algorithm: {str(decode_error)}"}
            )
    except Exception as e:
        print(f"[ERROR] Unexpected error in decode audio route: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Decoding failed: {str(e)}"}
        )

@router.post("/encode/direct")
async def encode_audio_direct(
    audio: UploadFile = File(...),
    message: str = Form(...)
):
    """
    Encode an audio file and serve it directly without S3 upload.
    This endpoint is a fallback for when S3 is not available.
    """
    try:
        # Log request info
        print(f"[INFO] Direct encode audio request received for file: {audio.filename}, content_type: {audio.content_type}")
        print(f"[INFO] Message length: {len(message)}")
        
        # Check file extension and content type
        valid_extensions = ['.wav', '.mp3']
        file_ext = os.path.splitext(audio.filename.lower())[1]
        
        # More permissive content type check
        is_valid_content_type = (
            audio.content_type.startswith("audio/") or 
            "audio" in audio.content_type.lower() or
            file_ext in valid_extensions
        )
        
        if not is_valid_content_type or file_ext not in valid_extensions:
            print(f"[WARNING] Invalid content type or file extension: {audio.content_type}, {file_ext}")
            return JSONResponse(
                status_code=400, 
                content={"detail": f"Only WAV or MP3 files are supported. Please upload a file with .wav or .mp3 extension. You uploaded a file with content type: {audio.content_type} and extension: {file_ext}"}
            )

        os.makedirs("temp", exist_ok=True)

        # Get file extension from the uploaded file
        file_ext = os.path.splitext(audio.filename.lower())[1]
        if not file_ext:
            file_ext = ".wav"  # Default to .wav if no extension
            
        # Generate unique paths with proper extensions
        input_path = f"temp/{uuid.uuid4()}{file_ext}"
        output_path = f"temp/{uuid.uuid4()}_encoded.wav"  # Output is always WAV
        
        print(f"[INFO] Using file extension: {file_ext}, input path: {input_path}")

        # Read and save the file
        file_content = await audio.read()
        print(f"[INFO] Read {len(file_content)} bytes from uploaded audio file")
        
        with open(input_path, "wb") as f:
            f.write(file_content)
            
        print(f"[INFO] Saved audio to {input_path}, file size: {os.path.getsize(input_path)} bytes")

        # Encode the message
        print(f"[INFO] Encoding message into audio: {input_path}")
        encode_audio(input_path, message, output_path)
        print(f"[INFO] Successfully encoded message, output file size: {os.path.getsize(output_path)} bytes")

        # Return the file directly
        return FileResponse(
            output_path,
            media_type="audio/wav",
            filename="encoded.wav"
        )
            
    except Exception as e:
        print(f"[ERROR] Unexpected error in direct encode audio route: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Direct encoding failed: {str(e)}"}
        )
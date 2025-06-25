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
        if audio.content_type not in ["audio/wav", "audio/x-wav", "audio/mp3"]:
            print(f"[WARNING] Invalid content type: {audio.content_type}")
            return JSONResponse(
                status_code=400, 
                content={"detail": "Only WAV or MP3 files are supported."}
            )

        os.makedirs("temp", exist_ok=True)

        input_ext = ".wav" if "wav" in audio.content_type else ".mp3"
        input_path = f"temp/{uuid.uuid4()}{input_ext}"
        output_path = f"temp/{uuid.uuid4()}_encoded.wav"

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
            print(f"[INFO] Encoding message into audio: {input_path}")
            encode_audio(input_path, message, output_path)
            print(f"[INFO] Successfully encoded message, output file size: {os.path.getsize(output_path)} bytes")
        except Exception as encode_error:
            print(f"[ERROR] Encoding algorithm failed: {encode_error}")
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
        
        if audio.content_type not in ["audio/wav", "audio/x-wav", "audio/mp3"]:
            print(f"[WARNING] Invalid content type: {audio.content_type}")
            return JSONResponse(
                status_code=400, 
                content={"detail": "Only WAV or MP3 files are supported."}
            )

        os.makedirs("temp", exist_ok=True)

        input_ext = ".wav" if "wav" in audio.content_type else ".mp3"
        input_path = f"temp/{uuid.uuid4()}{input_ext}"

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
        
        # Validate the audio file
        if audio.content_type not in ["audio/wav", "audio/x-wav", "audio/mp3"]:
            print(f"[WARNING] Invalid content type: {audio.content_type}")
            return JSONResponse(
                status_code=400, 
                content={"detail": "Only WAV or MP3 files are supported."}
            )

        os.makedirs("temp", exist_ok=True)

        input_ext = ".wav" if "wav" in audio.content_type else ".mp3"
        input_path = f"temp/{uuid.uuid4()}{input_ext}"
        output_path = f"temp/{uuid.uuid4()}_encoded.wav"

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
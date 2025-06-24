from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from routes import encode, decode
from routes import audio
from routes import image_file
from routes import video
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add a root endpoint for health checks and API information
@app.get("/")
async def root():
    from fastapi.responses import JSONResponse
    
    # For API clients
    return JSONResponse({
        "status": "online",
        "message": "Welcome to Steganography API",
        "version": "1.0.0",
        "frontend_url": "https://steganography-frontend.onrender.com",
        "endpoints": {
            "encode": "/encode/image",
            "decode": "/decode/image",
            "audio": "/audio/encode, /audio/decode",
            "image_file": "/image-file/encode, /image-file/decode",
            "video": "/video/encode, /video/decode",
            "docs": "/docs"
        }
    })

# Add a page endpoint for human visitors
@app.get("/info", response_class=HTMLResponse)
async def info_page():
    from fastapi.responses import HTMLResponse
    
    with open("static/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

app.include_router(encode.router, prefix="/encode")
app.include_router(decode.router, prefix="/decode")  # Added prefix to be consistent
app.include_router(audio.router, prefix="/audio")
app.include_router(image_file.router, prefix="/image-file")
app.include_router(video.router, prefix="/video")

# Print a message to help with debugging
print("API Routes configured:")
print("- /encode/image")
print("- /decode/image")
print("- /audio/encode, /audio/decode")
print("- /image-file/encode, /image-file/decode")
print("- /video/encode, /video/decode")
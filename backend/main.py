from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
import traceback

from routes import encode, decode, audio, image_file, video

import os

app = FastAPI()

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    print(f"[ERROR] HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"[ERROR] Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": f"Invalid request: {str(exc)}"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    print(f"[ERROR] Unhandled exception: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
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

@app.get("/info", response_class=HTMLResponse)
async def info_page():
    with open("static/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# ✅ Routers
app.include_router(encode.router, prefix="/encode")
app.include_router(decode.router, prefix="/decode")
app.include_router(audio.router, prefix="/audio")
app.include_router(image_file.router, prefix="/image-file")
app.include_router(video.router, prefix="/video")  # Fixed spelling: vedio → video

print("\nAPI Routes registered:")
for route in app.routes:
    if hasattr(route, "methods") and hasattr(route, "path"):
        print(f"- {', '.join(route.methods)}: {route.path}")

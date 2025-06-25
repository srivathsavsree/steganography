from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse

from routes import encode, decode, audio, image_file, vedio  # ✅ Fixed spelling here

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
app.include_router(vedio.router, prefix="/video")  # ✅ Correct spelling

print("\nAPI Routes registered:")
for route in app.routes:
    if hasattr(route, "methods") and hasattr(route, "path"):
        print(f"- {', '.join(route.methods)}: {route.path}")

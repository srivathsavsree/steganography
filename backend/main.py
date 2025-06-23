from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import encode, decode
from routes import audio
from routes import image_file
from routes import video

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(encode.router)
app.include_router(decode.router)  # Removed prefix to match /decode/image
app.include_router(audio.router, prefix="/audio")
app.include_router(image_file.router, prefix="/image-file")
app.include_router(video.router, prefix="/video")
from fastapi import FastAPI
from routes import encode, decode
from routes import audio
from routes import image_file
from routes import video

app = FastAPI()

app.include_router(encode.router, prefix="/encode")
app.include_router(decode.router, prefix="/decode")
app.include_router(audio.router, prefix="/audio")
app.include_router(image_file.router, prefix="/image-file")
app.include_router(video.router, prefix="/video")
import os
import shutil
import asyncio
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import FileResponse
import whisper
from deep_translator import GoogleTranslator
import edge_tts

app = FastAPI()

model = whisper.load_model("tiny")
UPLOAD_DIR = "./temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"status": "Server is running perfectly!"}

@app.post("/dub/")
async def dub_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_lang: str = Form("ar"),
    voice: str = Form("ar-SY-LaithNeural")
):
    return {"filename": file.filename, "message": "Processing..."}

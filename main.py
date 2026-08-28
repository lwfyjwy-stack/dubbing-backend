import os
import shutil
import asyncio
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
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
  video_path = os.path.join(UPLOAD_DIR, file.filename)
    audio_path = os.path.join(UPLOAD_DIR, "extracted.wav")
    dub_audio_path = os.path.join(UPLOAD_DIR, "dubbed.mp3")
    output_video_path = os.path.join(UPLOAD_DIR, f"dubbed_{file.filename}")
with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
  result = model.transcribe(video_path)
translator = GoogleTranslator(source='auto', target=target_lang)
    translated_texts = [translator.translate(s['text'].strip()) for s in result['segments'] if s['text'].strip()]
    full_text = " ".join(translated_texts)
communicate = edge_tts.Communicate(full_text, voice)
    await communicate.save(dub_audio_path)
os.system(f'ffmpeg -y -i "{video_path}" -i "{dub_audio_path}" -c:v copy -map 0:v:0 -map 1:a:0 "{output_video_path}"')
def cleanup():
  for path in [video_path, audio_path, dub_audio_path, output_video_path]:
            if os.path.exists(path):
                os.remove(path)
              background_tasks.add_task(cleanup)
    
    return FileResponse(output_video_path

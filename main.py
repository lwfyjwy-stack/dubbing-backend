import os
import subprocess
from fastapi import FastAPI, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse
from gtts import gTTS

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_video_task(input_video_path: str, output_video_path: str):
    try:
        print("--- بدأ عملية توليد الصوت واستبدال الصوت الأصلي بالكامل ---")
        
        # 1. توليد ملف الصوت العربي
        tts = gTTS(text="مرحباً بك، هذه هي الدبلجة العربية الجديدة.", lang="ar")
        voice_path = os.path.join(OUTPUT_DIR, "temp_voice.mp3")
        tts.save(voice_path)
        print(f"--- تم توليد الصوت بنجاح في: {voice_path} ---")

        # 2. استبدال صوت الفيديو الأصلي بالصوت الجديد فقط (حذف الصوت القديم كلياً)
        cmd = [
            "ffmpeg", "-y",
            "-i", input_video_path,
            "-i", voice_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            output_video_path
        ]
        
        subprocess.run(cmd, check=True)
        print(f"--- انتهت عملية الدبلجة واستبدال الصوت بنجاح في: {output_video_path} ---")

    except Exception as e:
        print(f"--- خطأ أثناء معالجة الفيديو: {e} ---")

@app.post("/dub/")
async def dub_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    output_filename = f"dubbed_{file.filename}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    with open(input_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    background_tasks.add_task(process_video_task, input_path, output_path)

    return {
        "message": "تم استلام الفيديو وبدء عملية الدبلجة الفردية في الخلفية!",
        "download_url": f"/download/{output_filename}"
    }

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4", filename=filename)
    return {"error": "الملف غير موجود أو لم تكتمل معالجته بعد"}

import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

# مجلدات لحفظ الملفات المؤقتة والنتائج
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def background_dubbing_task(input_path: str, output_path: str, target_lang: str, voice: str):
    try:
        # هنا يتم استدعاء دالة معالجة الفيديو والدبلجة الفعلية الخاصة بك
        # process_video_pipeline(input_path, output_path, target_lang, voice)
        
        # محاكاة مؤقتة للمعالجة (حتى تربط دالتك الحقيقية)
        shutil.copy(input_path, output_path) 
        
    except Exception as e:
        print(f"Error in background task: {e}")
    finally:
        # تنظيف ملف الإدخال المؤقت لتوفير مساحة الـ RAM
        if os.path.exists(input_path):
            os.remove(input_path)

@app.get("/")
def home():
    return {"status": "Server is running perfectly!"}

@app.post("/dub/")
async def dub_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_lang: str = Form(...),
    voice: str = Form(...)
):
    input_file_path = os.path.join(UPLOAD_DIR, file.filename)
    output_filename = f"dubbed_{file.filename}"
    output_file_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # حفظ الملف المرفوع مؤقتًا على القرص
    with open(input_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # تشغيل الدبلجة في الخلفية لتجنب حدوث Timeout
    background_tasks.add_task(
        background_dubbing_task, 
        input_file_path, 
        output_file_path, 
        target_lang, 
        voice
    )
    
    return {
        "message": "Video is processing in the background.",
        "filename": output_filename,
        "download_url": f"/download/{output_filename}"
    }

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4", filename=filename)
    raise HTTPException(status_code=404, detail="File not found or still processing.")

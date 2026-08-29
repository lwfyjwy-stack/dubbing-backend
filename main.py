import os
import shutil
import traceback
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

# مسارات الحفظ المؤقتة
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==========================================
# دالة معالجة الدبلجة في الخلفية (آمنة وخفيفة)
# ==========================================
async def background_dubbing_task(input_file_path: str, output_file_path: str, target_lang: str, voice: str):
    try:
        print(f"--- بدأ معالجة الفيديو في الخلفية للغة: {target_lang} والصوت: {voice} ---")
        
        # حالياً نقوم بنسخ الملف المرفوع كنموذج تجريبي للتأكد من نجاح المسار
        shutil.copy(input_file_path, output_file_path)

        print(f"--- تم الانتهاء من المعالجة بنجاح وحفظه في: {output_file_path} ---")

    except Exception as e:
        print(f"❌ حدث خطأ أثناء معالجة الفيديو في الخلفية: {str(e)}")
        print(traceback.format_exc())


# ==========================================
# نقطة النهاية (API) لاستقبال الفيديو
# ==========================================
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

    # حفظ الملف المرفوع مؤقتا على القرص
    with open(input_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # تشغيل المهمة في الخلفية
    background_tasks.add_task(
        background_dubbing_task,
        input_file_path,
        output_file_path,
        target_lang,
        voice
    )

    return {
        "message": "Video is processing in the background safely.",
        "filename": output_filename,
        "download_url": f"/download/{output_filename}"
    }


# ==========================================
# نقطة النهاية (API) لتحميل الفيديو
# ==========================================
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found or still processing.")

import os
import shutil
import traceback
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from gtts import gTTS

app = FastAPI()

# مسارات الحفظ المؤقتة
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==========================================
# دالة معالجة الدبلجة وتوليد الصوت في الخلفية
# ==========================================
async def background_dubbing_task(input_file_path: str, output_file_path: str, target_lang: str, voice: str):
    try:
        print(f"--- بدأ معالجة الفيديو والدبلجة للغة: {target_lang} والصوت: {voice} ---")
        
        # 1. سنقوم بتوليد صوت تجريبي (كمثال: تحويل نص إلى صوت باللغة العربية)
        # يمكنك لاحقاً استبدال هذا النص بالنص المترجم المستخرج من الفيديو
        sample_text = "هذه تجربة دبلجة صوتية تلقائية للسيرفر."
        
        audio_output_path = os.path.join(OUTPUT_DIR, "temp_voice.mp3")
        
        # توليد الصوت باستخدام gTTS (اللغة العربية ar)
        tts = gTTS(text=sample_text, lang='ar', slow=False)
        tts.save(audio_output_path)
        print(f"--- تم توليد الصوت بنجاح في: {audio_output_path} ---")

        # حالياً نقوم بنسخ الفيديو الأصلي مع حفظ مسار الصوت الناتج جنباً إلى جنب
        # (في الخطوات القادمة سنقوم بدمج ملف الصوت مع الفيديو بـ ffmpeg)
        shutil.copy(input_file_path, output_file_path)

        print(f"--- انتهت عملية الدبلجة وحفظ الفيديو في: {output_file_path} ---")

    except Exception as e:
        print(f"❌ حدث خطأ أثناء الدبلجة في الخلفية: {str(e)}")
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
        "message": "Dubbing process started in the background successfully.",
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

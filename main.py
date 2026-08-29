import os
import shutil
import traceback
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from moviepy.editor import VideoFileClip

app = FastAPI()

# مسارات الحفظ المؤقتة
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==========================================
# دالة معالجة الدبلجة الفعليّة في الخلفية
# ==========================================
async def background_dubbing_task(input_file_path: str, output_file_path: str, target_lang: str, voice: str):
    try:
        print(f"--- بدأ معالجة الفيديو في الخلفية للغة: {target_lang} والصوت: {voice} ---")
        
        # مثال عملي باستخدام MoviePy لفتح الفيديو ومعالجته
        # (يمكنك استبدال هذا الجزء بكود الذكاء الاصطناعي الخاص بالترجمة وتوليد الصوت)
        clip = VideoFileClip(input_file_path)
        
        # هنا يتم تطبيق عمليات الدبلجة (توليد الصوت الجديد ودمجه مع الفيديو)
        # للتجربة حالياً، سنقوم بحفظ نسخة معالجة أو كتم الصوت/تعديله
        final_clip = clip # ضع كود دمج الصوت المترجم هنا
        
        # حفظ الفيديو الناتج في المسار النهائي المطلوب
        final_clip.write_videofile(output_file_path, codec="libx264", audio_codec="aac")
        
        # إغلاق الملفات لتحرير الذاكرة
        clip.close()

        print(f"--- تم الانتهاء من دبلجة الفيديو بنجاح وحفظه في: {output_file_path} ---")

    except Exception as e:
        # تسجيل أي خطأ مفصل في الـ Logs بدلاً من التوقف بصمت
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


# ==========================================
# نقطة النهاية (API) لتحميل الفيديو بعد انتهائه
# ==========================================
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found or still processing.")

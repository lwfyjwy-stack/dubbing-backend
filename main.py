import os
import shutil
import asyncio
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
import whisper
from deep_translator import GoogleTranslator
import edge_tts

app = FastAPI()

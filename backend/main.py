from fastapi import FastAPI, UploadFile, File
import shutil
import os

from backend.resume_parser import extract_text
from backend.interview import generate_questions

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "AI Interview Copilot API is Running 🚀"
    }


@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume and extract text.
    """

    # Save uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract resume text
    resume_text = extract_text(file_path)

    # Generate interview questions
    questions = generate_questions(resume_text)

    return {
        "filename": file.filename,
        "resume_text": resume_text,
        "questions": questions
    }
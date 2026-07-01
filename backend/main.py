from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import shutil
import os

from backend.resume_parser import extract_text
from backend.interview import generate_questions
from backend.evaluator import evaluate_answer

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
    Upload resume and generate interview questions.
    """

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resume_text = extract_text(file_path)

    questions = generate_questions(resume_text)

    return {
        "filename": file.filename,
        "resume_text": resume_text,
        "questions": questions
    }


class InterviewRequest(BaseModel):
    question: str
    answer: str


@app.post("/evaluate")
def evaluate(request: InterviewRequest):

    feedback = evaluate_answer(
        request.question,
        request.answer
    )

    return feedback
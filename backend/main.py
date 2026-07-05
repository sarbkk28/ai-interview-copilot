from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

import os
import shutil

from backend.evaluator import evaluate_answer
from backend.interview import generate_questions
from backend.resume_parser import extract_text


app = FastAPI(
    title="AI Interview Copilot API",
    version="2.0"
)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class InterviewRequest(BaseModel):
    question: str
    answer: str


@app.get("/")
def home():
    return {
        "message": "AI Interview Copilot API is Running 🚀"
    }


@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume, extract its text and generate interview questions.
    """

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    resume_text = extract_text(file_path)

    questions = generate_questions(
        resume_text
    )

    return {
        "filename": file.filename,
        "resume_text": resume_text,
        "questions": questions
    }


@app.post("/evaluate")
def evaluate(request: InterviewRequest):
    """
    Evaluate a candidate's interview answer.
    """

    feedback = evaluate_answer(
        question=request.question,
        answer=request.answer
    )

    return feedback
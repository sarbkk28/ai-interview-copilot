import os
import shutil

from fastapi import FastAPI
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from pydantic import BaseModel

from backend.evaluator import evaluate_answer
from backend.interview import generate_adaptive_question
from backend.interview import generate_questions
from backend.resume_parser import extract_text


app = FastAPI(
    title="AI Interview Copilot API",
    description=(
        "AI-powered adaptive interview backend."
    ),
    version="2.0"
)


UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx"
}


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


class InterviewRequest(BaseModel):
    question: str
    answer: str


class AdaptiveQuestionRequest(BaseModel):
    previous_question: str
    previous_answer: str
    score: float
    weaknesses: list[str]


@app.get("/")
def home():

    return {
        "message": (
            "AI Interview Copilot API "
            "is Running 🚀"
        )
    }


@app.post("/upload_resume")
async def upload_resume(
    file: UploadFile = File(...)
):
    """
    Upload a resume and generate
    personalized interview questions.
    """

    try:

        extension = os.path.splitext(
            file.filename
        )[1].lower()

        if extension not in ALLOWED_EXTENSIONS:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only PDF and DOCX "
                    "resumes are supported."
                )
            )

        safe_filename = os.path.basename(
            file.filename
        )

        file_path = os.path.join(
            UPLOAD_FOLDER,
            safe_filename
        )

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        resume_text = extract_text(
            file_path
        )

        questions = generate_questions(
            resume_text
        )

        return {
            "filename": safe_filename,
            "resume_text": resume_text,
            "questions": questions
        }

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        ) from error


@app.post("/evaluate")
def evaluate(
    request: InterviewRequest
):
    """
    Evaluate a candidate's answer.
    """

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    if not request.answer.strip():

        raise HTTPException(
            status_code=400,
            detail="Answer cannot be empty."
        )

    try:

        feedback = evaluate_answer(
            question=request.question,
            answer=request.answer
        )

        return feedback

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        ) from error


@app.post("/adaptive_question")
def adaptive_question(
    request: AdaptiveQuestionRequest
):
    """
    Generate a performance-based
    adaptive interview question.
    """

    try:

        question = generate_adaptive_question(
            previous_question=(
                request.previous_question
            ),
            previous_answer=(
                request.previous_answer
            ),
            score=request.score,
            weaknesses=request.weaknesses
        )

        return {
            "question": question
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        ) from error
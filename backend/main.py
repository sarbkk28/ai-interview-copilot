import os
import shutil

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.responses import Response
from pydantic import BaseModel

from backend.database import initialize_database
from backend.evaluator import evaluate_answer
from backend.followup import generate_followup_decision
from backend.interview import (
    generate_adaptive_question,
    generate_questions,
)
from backend.models import (
    complete_interview,
    create_interview,
    get_all_interviews,
    get_interview_answers,
    save_interview_answer,
)
from backend.report_generator import (
    generate_interview_report,
)
from backend.resume_parser import extract_text
from backend.roadmap import generate_prep_roadmap
from backend.transcription import transcribe_audio


# ==================================================
# FASTAPI APP
# ==================================================


app = FastAPI(
    title="AI Interview Copilot API",
    description=(
        "Resume-based adaptive AI "
        "mock interview API."
    ),
    version="1.0.0",
)


# ==================================================
# DATABASE
# ==================================================


initialize_database()


# ==================================================
# UPLOAD DIRECTORY
# ==================================================


UPLOAD_FOLDER = "uploads"


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True,
)


# ==================================================
# REQUEST MODELS
# ==================================================


class EvaluationRequest(BaseModel):

    interview_id: int

    question_number: int

    topic: str

    question: str

    answer: str


class AdaptiveQuestionRequest(BaseModel):

    previous_question: str

    previous_answer: str

    score: float

    weaknesses: list[str]

    next_topic: str

    target_role: str


class FollowUpDecisionRequest(BaseModel):

    question: str

    answer: str

    score: float

    weaknesses: list[str]

    topic: str


class CompleteInterviewRequest(BaseModel):

    interview_id: int


# ==================================================
# HOME
# ==================================================


@app.get("/")
def home():

    return {
        "message": (
            "AI Interview Copilot API "
            "is Running 🚀"
        )
    }


# ==================================================
# HEALTH CHECK
# ==================================================


@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "AI Interview Copilot",
    }


# ==================================================
# UPLOAD RESUME
# ==================================================


@app.post("/upload_resume")
async def upload_resume(
    file: UploadFile = File(...),
    target_role: str = "AI Engineer",
):

    try:

        if not file.filename:

            raise HTTPException(
                status_code=400,
                detail="Resume filename is missing.",
            )


        allowed_extensions = (
            ".pdf",
            ".docx",
        )


        file_extension = os.path.splitext(
            file.filename
        )[1].lower()


        if (
            file_extension
            not in allowed_extensions
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only PDF and DOCX "
                    "resumes are supported."
                ),
            )


        file_path = os.path.join(
            UPLOAD_FOLDER,
            file.filename,
        )


        with open(
            file_path,
            "wb",
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer,
            )


        resume_text = extract_text(
            file_path
        )


        if not resume_text:

            raise ValueError(
                "No text could be extracted "
                "from the resume."
            )


        if not resume_text.strip():

            raise ValueError(
                "Extracted resume text is empty."
            )


        questions = generate_questions(
            resume_text=resume_text,
            target_role=target_role,
        )


        if not questions:

            raise ValueError(
                "No interview questions "
                "were generated."
            )


        interview_id = create_interview(
            resume_filename=file.filename
        )


        return {
            "interview_id": interview_id,
            "filename": file.filename,
            "resume_text": resume_text,
            "target_role": target_role,
            "questions": questions,
        }


    except HTTPException:

        raise


    except Exception as error:

        print(
            "UPLOAD RESUME ERROR:",
            repr(error),
        )


        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


# ==================================================
# AUDIO TRANSCRIPTION
# ==================================================


@app.post("/transcribe")
async def transcribe_interview_answer(
    file: UploadFile = File(...),
):

    try:

        if not file.filename:

            raise HTTPException(
                status_code=400,
                detail="Audio filename is missing.",
            )


        allowed_extensions = (
            ".wav",
            ".mp3",
            ".m4a",
            ".webm",
            ".ogg",
        )


        file_extension = os.path.splitext(
            file.filename
        )[1].lower()


        if (
            file_extension
            not in allowed_extensions
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Unsupported audio format."
                ),
            )


        audio_bytes = await file.read()


        if not audio_bytes:

            raise HTTPException(
                status_code=400,
                detail="Audio file is empty.",
            )


        transcript = transcribe_audio(
            audio_bytes=audio_bytes,
            filename=file.filename,
        )


        return {
            "transcript": transcript
        }


    except HTTPException:

        raise


    except Exception as error:

        print(
            "TRANSCRIBE ENDPOINT ERROR:",
            repr(error),
        )


        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


# ==================================================
# EVALUATE ANSWER
# ==================================================


@app.post("/evaluate")
def evaluate(
    request: EvaluationRequest,
):

    try:

        if not request.topic.strip():

            raise HTTPException(
                status_code=400,
                detail="Topic cannot be empty.",
            )


        if not request.question.strip():

            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty.",
            )


        if not request.answer.strip():

            raise HTTPException(
                status_code=400,
                detail="Answer cannot be empty.",
            )


        feedback = evaluate_answer(
            question=request.question,
            answer=request.answer,
        )


        save_interview_answer(
            interview_id=request.interview_id,
            question_number=request.question_number,
            topic=request.topic,
            question=request.question,
            answer=request.answer,
            feedback=feedback,
        )


        return feedback


    except HTTPException:

        raise


    except Exception as error:

        print(
            "ANSWER EVALUATION ERROR:",
            repr(error),
        )


        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


# ==================================================
# ADAPTIVE QUESTION
# ==================================================


@app.post("/adaptive_question")
def adaptive_question(
    request: AdaptiveQuestionRequest,
):

    try:

        if not request.next_topic.strip():

            raise HTTPException(
                status_code=400,
                detail=(
                    "Next topic cannot be empty."
                ),
            )


        question = generate_adaptive_question(
            previous_question=(
                request.previous_question
            ),
            previous_answer=(
                request.previous_answer
            ),
            score=request.score,
            weaknesses=request.weaknesses,
            next_topic=request.next_topic,
            target_role=request.target_role,
        )


        return {
            "question": question
        }


    except HTTPException:

        raise


    except Exception as error:

        print(
            "ADAPTIVE QUESTION ERROR:",
            repr(error),
        )


        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error




# ==================================================
# FOLLOW-UP DECISION
# ==================================================


@app.post("/followup_decision")
def followup_decision(
    request: FollowUpDecisionRequest,
):

    try:

        if not request.question.strip():

            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty.",
            )

        if not request.answer.strip():

            raise HTTPException(
                status_code=400,
                detail="Answer cannot be empty.",
            )

        if not request.topic.strip():

            raise HTTPException(
                status_code=400,
                detail="Topic cannot be empty.",
            )

        decision = generate_followup_decision(
            question=request.question,
            answer=request.answer,
            score=request.score,
            weaknesses=request.weaknesses,
            topic=request.topic,
        )

        return decision

    except HTTPException:

        raise

    except Exception as error:

        print(
            "FOLLOW-UP DECISION ERROR:",
            repr(error),
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


# ==================================================
# COMPLETE INTERVIEW
# ==================================================


@app.post("/complete_interview")
def finish_interview(
    request: CompleteInterviewRequest,
):

    try:

        average_score = complete_interview(
            interview_id=request.interview_id
        )


        return {
            "interview_id": (
                request.interview_id
            ),
            "completed": True,
            "overall_score": average_score,
        }


    except Exception as error:

        print(
            "COMPLETE INTERVIEW ERROR:",
            repr(error),
        )


        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


# ==================================================
# INTERVIEW HISTORY
# ==================================================


@app.get("/interviews")
def interview_history():

    try:

        interviews = get_all_interviews()


        return {
            "interviews": interviews
        }


    except Exception as error:

        print(
            "INTERVIEW HISTORY ERROR:",
            repr(error),
        )


        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


# ==================================================
# INTERVIEW DETAILS
# ==================================================


@app.get("/interviews/{interview_id}")
def interview_details(
    interview_id: int,
):

    try:

        answers = get_interview_answers(
            interview_id=interview_id
        )


        return {
            "interview_id": interview_id,
            "answers": answers,
        }


    except Exception as error:

        print(
            "INTERVIEW DETAILS ERROR:",
            repr(error),
        )


        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


# ==================================================
# PDF INTERVIEW REPORT
# ==================================================


@app.get(
    "/interviews/{interview_id}/report"
)
def download_interview_report(
    interview_id: int,
):

    try:

        answers = get_interview_answers(
            interview_id=interview_id
        )


        if not answers:

            raise HTTPException(
                status_code=404,
                detail=(
                    "No interview answers "
                    "found for this interview."
                ),
            )


        pdf_data = generate_interview_report(
            interview_id=interview_id,
            answers=answers,
        )


        filename = (
            f"interview_report_"
            f"{interview_id}.pdf"
        )


        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f'attachment; '
                    f'filename="{filename}"'
                )
            },
        )


    except HTTPException:

        raise


    except Exception as error:

        print(
            "REPORT GENERATION ERROR:",
            repr(error),
        )


        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


# ==================================================
# AI PREP ROADMAP
# ==================================================


@app.post("/prep_roadmap")
def prep_roadmap():

    try:

        interviews = get_all_interviews()


        if not interviews:

            raise HTTPException(
                status_code=404,
                detail=(
                    "No interview history found."
                ),
            )


        interview_history = []


        for interview in interviews:

            interview_id = interview["id"]


            answers = get_interview_answers(
                interview_id=interview_id
            )


            for answer in answers:

                interview_history.append(
                    {
                        "interview_id": interview_id,
                        "topic": answer.get(
                            "topic"
                        ),
                        "question": answer.get(
                            "question"
                        ),
                        "answer": answer.get(
                            "answer"
                        ),
                        "overall_score": answer.get(
                            "overall_score"
                        ),
                        "technical_accuracy": (
                            answer.get(
                                "technical_accuracy"
                            )
                        ),
                        "communication": answer.get(
                            "communication"
                        ),
                        "depth": answer.get(
                            "depth"
                        ),
                        "relevance": answer.get(
                            "relevance"
                        ),
                        "weaknesses": answer.get(
                            "weaknesses",
                            [],
                        ),
                        "topics_to_improve": answer.get(
                            "topics_to_improve",
                            [],
                        ),
                    }
                )


        if not interview_history:

            raise HTTPException(
                status_code=404,
                detail=(
                    "No saved interview answers "
                    "found. Submit at least one "
                    "interview answer first."
                ),
            )


        roadmap = generate_prep_roadmap(
            interview_history=interview_history
        )


        return {
            "total_answers_analyzed": (
                len(interview_history)
            ),
            "roadmap": roadmap,
        }


    except HTTPException:

        raise


    except Exception as error:

        print(
            "PREP ROADMAP ERROR:",
            repr(error),
        )


        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error
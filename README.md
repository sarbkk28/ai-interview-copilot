# AI Interview Copilot

An adaptive, role-based AI mock interview platform that personalizes
technical interviews from a candidate's resume, evaluates answers, asks
intelligent follow-up questions, and generates a personalized
preparation roadmap.

## Overview

AI Interview Copilot is a full-stack AI interview preparation system
designed to make mock interviews more realistic and personalized.

Instead of asking a fixed list of generic questions, the platform
analyzes a candidate's resume and selected target role, generates
role-specific interview questions, evaluates each response across
multiple dimensions, adapts the difficulty of future questions, and
decides whether an answer contains a technical claim or knowledge gap
worth probing with a targeted follow-up.

Candidates can answer by typing or speaking. Voice answers are
transcribed into editable text before evaluation.

## Key Features

-   Resume-based personalized interview question generation
-   Role-based modes: AI Engineer, ML Engineer, Data Scientist, Data
    Analyst, and Backend Engineer
-   Ten role-specific interview topics per interview
-   Adaptive question difficulty based on previous performance
-   Intelligent answer-aware follow-up question generation
-   Maximum one targeted follow-up per main question
-   Typed and voice interview answers
-   Groq Whisper speech-to-text transcription
-   Editable voice transcripts before submission
-   Multi-dimensional evaluation: Technical Accuracy, Communication,
    Depth, and Relevance
-   Strength and weakness identification
-   Improved answer generation
-   Interview history and performance analytics
-   Score trends and skill comparison charts
-   Downloadable PDF interview reports
-   AI-generated personalized 7-day preparation roadmap
-   Backend health monitoring
-   Separate frontend and backend deployment

## How It Works

1.  The candidate selects a target technical role.
2.  The candidate uploads a PDF or DOCX resume.
3.  The backend extracts resume text.
4.  Groq generates ten personalized, role-specific interview questions.
5.  The candidate answers using text or voice.
6.  Voice answers are transcribed and can be edited before submission.
7.  The answer is evaluated across technical accuracy, communication,
    depth, and relevance.
8.  The follow-up decision engine determines whether one targeted probe
    is useful.
9.  If needed, the interviewer asks an answer-aware follow-up question.
10. Otherwise, the next main question is adapted to previous
    performance.
11. Responses and scores are stored for analytics.
12. The candidate can download a PDF report and generate a personalized
    7-day preparation roadmap.

## System Architecture

``` text
                         Candidate
                             |
                             v
                    Streamlit Frontend
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
     Resume Upload      Text Answer        Voice Answer
          |                                      |
          |                                      v
          |                              Audio Transcription
          |                                Groq Whisper
          |                                      |
          +------------------+-------------------+
                             |
                             v
                      FastAPI Backend
                             |
          +------------------+-------------------+
          |                  |                   |
          v                  v                   v
  Resume Question       Answer Evaluation   Follow-up Decision
    Generation               Engine               Engine
          |                  |                   |
          +------------------+-------------------+
                             |
                             v
                    Adaptive Interview Engine
                             |
                             v
                      SQLite Persistence
                             |
          +------------------+-------------------+
          |                  |                   |
          v                  v                   v
       Analytics         PDF Reports       AI Prep Roadmap
```

## AI Interview Logic

``` text
Main Question
      |
      v
Candidate Answer
      |
      v
AI Evaluation
      |
      v
Follow-up Decision Engine
      |
      +---- Useful technical point or gap? ----+
      |                                        |
     Yes                                       No
      |                                        |
      v                                        v
Targeted Follow-up                     Adaptive Next Topic
      |
      v
Evaluate Follow-up
      |
      v
Adaptive Next Topic
```

The system allows at most one follow-up per main question to prevent the
interview from getting stuck on one topic.

## Role-Specific Interview Design

-   **AI Engineer:** machine learning, LLM engineering, RAG, AI
    evaluation, APIs, deployment, and AI system design.
-   **ML Engineer:** machine learning, feature engineering, model
    evaluation, ML pipelines, MLOps, deployment, and system design.
-   **Data Scientist:** statistics, ML, preprocessing, feature
    engineering, experimentation, and business problem solving.
-   **Data Analyst:** SQL, data cleaning, statistics, visualization,
    business analytics, dashboarding, and case studies.
-   **Backend Engineer:** DSA, backend development, APIs, databases,
    security, scalability, deployment, and system design.

## Tech Stack

  Layer                 Technology
  --------------------- ---------------------------
  Frontend              Streamlit
  Backend               FastAPI
  LLM                   Groq with Llama 3.3 70B
  Speech-to-Text        Groq Whisper
  Database              SQLite
  Data Analysis         Pandas
  PDF Reports           ReportLab
  Resume Parsing        PDF and DOCX parsing
  Backend Deployment    Render
  Frontend Deployment   Streamlit Community Cloud
  Version Control       Git and GitHub

## Project Structure

``` text
ai-interview-copilot/
|-- backend/
|   |-- __init__.py
|   |-- main.py
|   |-- interview.py
|   |-- followup.py
|   |-- evaluator.py
|   |-- transcription.py
|   |-- resume_parser.py
|   |-- database.py
|   |-- models.py
|   |-- roadmap.py
|   `-- report_generator.py
|-- frontend/
|   `-- app.py
|-- requirements.txt
|-- .gitignore
`-- README.md
```

## Local Setup

### 1. Clone the repository

``` bash
git clone <YOUR_REPOSITORY_URL>
cd ai-interview-copilot
```

### 2. Create and activate a virtual environment

``` bash
python -m venv .venv
```

On Windows:

``` powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

``` text
GROQ_API_KEY=your_groq_api_key
```

Never commit the `.env` file.

### 5. Start FastAPI

``` bash
uvicorn backend.main:app --port 8001 --reload
```

### 6. Start Streamlit

In a second terminal:

``` bash
streamlit run frontend/app.py
```

## API Endpoints

  -------------------------------------------------------------------------------------
  Method                  Endpoint                              Purpose
  ----------------------- ------------------------------------- -----------------------
  GET                     `/`                                   API status

  GET                     `/health`                             Backend health check

  POST                    `/upload_resume`                      Parse resume and
                                                                generate interview

  POST                    `/transcribe`                         Convert recorded answer
                                                                to text

  POST                    `/evaluate`                           Evaluate and save an
                                                                answer

  POST                    `/followup_decision`                  Decide whether to ask a
                                                                targeted follow-up

  POST                    `/adaptive_question`                  Generate an adaptive
                                                                next-topic question

  POST                    `/complete_interview`                 Complete an interview
                                                                and calculate its score

  GET                     `/interviews`                         Retrieve interview
                                                                history

  GET                     `/interviews/{interview_id}`          Retrieve interview
                                                                details

  GET                     `/interviews/{interview_id}/report`   Generate a PDF
                                                                interview report

  POST                    `/prep_roadmap`                       Generate a personalized
                                                                preparation roadmap
  -------------------------------------------------------------------------------------

## Deployment

The application uses separate frontend and backend deployments:

-   Backend: Render
-   Frontend: Streamlit Community Cloud

The Streamlit frontend communicates with the public FastAPI backend
through REST API requests.

## Security Notes

-   API keys are stored in environment variables.
-   `.env` is excluded using `.gitignore`.
-   Uploaded resumes should not be committed.
-   Production secrets should be configured through deployment
    environment variables.

## Future Improvements

The v1.0 feature set is frozen. Future versions may explore persistent
cloud database storage, authentication, session ownership, more roles,
configurable interview length, production observability, automated
integration tests, and advanced semantic performance tracking.

## Author

**Sarbani Kundu**

AI/ML enthusiast and engineering student building practical AI systems.

## License

This project is currently provided for educational and portfolio
purposes.

import json
import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_questions(resume_text: str) -> list[str]:
    """
    Generate personalized interview questions
    based on the candidate's resume.
    """

    prompt = f"""
You are an experienced senior technical interviewer.

Generate exactly 10 personalized interview questions
based on the candidate's resume.

Rules:
- Questions must be related to skills, projects,
  technologies, research, and experience in the resume.
- Include technical and behavioral questions.
- Start with easier questions.
- Gradually increase difficulty.
- Do not provide answers.
- Do not number the questions.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "questions": [
        "Question one",
        "Question two",
        "Question three",
        "Question four",
        "Question five",
        "Question six",
        "Question seven",
        "Question eight",
        "Question nine",
        "Question ten"
    ]
}}

Candidate Resume:

{resume_text}

Return JSON only.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    result = response.choices[0].message.content

    parsed_result = json.loads(result)

    return parsed_result["questions"]


def generate_adaptive_question(
    previous_question: str,
    previous_answer: str,
    score: float,
    weaknesses: list[str]
) -> str:
    """
    Generate an adaptive follow-up question
    based on candidate performance.
    """

    if score >= 8:

        difficulty_instruction = """
The candidate performed very well.

Ask a harder technical follow-up question.

The question should test:
- deeper technical understanding
- optimization
- scalability
- trade-offs
- real-world implementation
"""

    elif score <= 5:

        difficulty_instruction = """
The candidate struggled with the previous question.

Ask an easier foundational question
related to the same topic.

Test whether the candidate understands
the basic concept.
"""

    else:

        difficulty_instruction = """
The candidate performed reasonably well.

Ask a medium-difficulty follow-up question
related to the same topic.

Explore the candidate's understanding further.
"""

    prompt = f"""
You are an adaptive senior technical interviewer.

Previous Question:
{previous_question}

Candidate Answer:
{previous_answer}

Candidate Score:
{score}/10

Candidate Weak Areas:
{weaknesses}

{difficulty_instruction}

Rules:

- Ask exactly ONE interview question.
- The question must relate to the previous topic.
- Do not provide an answer.
- Do not explain the question.
- Do not number the question.
- Return only the question text.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.5
    )

    return response.choices[0].message.content.strip()
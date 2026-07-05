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
    Generate personalized interview questions from resume text.
    """

    prompt = f"""
You are an experienced technical interviewer.

Generate exactly 10 personalized interview questions based on the
candidate's resume.

Rules:
- Questions must be based on skills and projects in the resume.
- Include technical and behavioral questions.
- Start easy.
- Gradually increase difficulty.
- Do not include answers.
- Do not number questions.

Return ONLY valid JSON using exactly this format:

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

Resume:

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
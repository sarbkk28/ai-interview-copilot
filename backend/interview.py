import json
import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY is missing from .env"
    )


client = Groq(
    api_key=api_key
)


INTERVIEW_TOPICS = [
    "resume introduction",
    "machine learning",
    "project experience",
    "backend and APIs",
    "LLM and AI engineering",
    "data structures and algorithms",
    "deployment and production",
    "research or technical depth",
    "behavioral",
    "system design"
]


def generate_questions(
    resume_text: str
) -> list[dict]:

    print("🔥 generate_questions() running")

    prompt = f"""
You are a senior technical interviewer.

Generate exactly 10 personalized interview questions
based on the candidate resume.

The interview must contain exactly one question
for each of these topics:

{json.dumps(INTERVIEW_TOPICS)}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "questions": [
        {{
            "topic": "resume introduction",
            "question": "Question text"
        }},
        {{
            "topic": "machine learning",
            "question": "Question text"
        }}
    ]
}}

Rules:

- Return exactly 10 question objects.
- Use the exact topics provided.
- Generate one question per topic.
- Personalize questions using the resume.
- Do not provide answers.
- Do not use markdown.
- Do not use code fences.
- Return JSON only.

Candidate Resume:

{resume_text}
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a technical interviewer. "
                        "Always return valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            response_format={
                "type": "json_object"
            }
        )

    except Exception as error:

        print(
            "❌ GROQ API ERROR:",
            repr(error)
        )

        raise ValueError(
            f"Groq API failed: {error}"
        ) from error


    raw_response = (
        response
        .choices[0]
        .message
        .content
    )


    print(
        "🔥 RAW GROQ RESPONSE:"
    )

    print(
        repr(raw_response)
    )


    if raw_response is None:

        raise ValueError(
            "Groq returned None."
        )


    if not raw_response.strip():

        raise ValueError(
            "Groq returned an empty response."
        )


    try:

        parsed_response = json.loads(
            raw_response
        )

    except json.JSONDecodeError as error:

        print(
            "❌ JSON PARSING FAILED"
        )

        print(
            "RAW RESPONSE:"
        )

        print(
            repr(raw_response)
        )

        raise ValueError(
            "Groq returned invalid JSON. "
            f"JSON error: {error}"
        ) from error


    questions = parsed_response.get(
        "questions"
    )


    if not isinstance(
        questions,
        list
    ):

        raise ValueError(
            "The AI response does not contain "
            "a questions list."
        )


    if len(questions) != 10:

        raise ValueError(
            f"Expected 10 questions. "
            f"Received {len(questions)}."
        )


    validated_questions = []


    for index, topic in enumerate(
        INTERVIEW_TOPICS
    ):

        question_data = questions[index]


        if not isinstance(
            question_data,
            dict
        ):

            raise ValueError(
                f"Question {index + 1} "
                "has an invalid structure."
            )


        question = question_data.get(
            "question"
        )


        if not question:

            raise ValueError(
                f"Question {index + 1} "
                "is empty."
            )


        validated_questions.append(
            {
                "topic": topic,
                "question": question.strip()
            }
        )


    return validated_questions


def generate_adaptive_question(
    previous_question: str,
    previous_answer: str,
    score: float,
    weaknesses: list[str],
    next_topic: str
) -> str:

    if score >= 8:

        difficulty = "hard"

        difficulty_instruction = """
Ask a challenging question testing deeper reasoning,
trade-offs, scalability, optimization, or production knowledge.
"""

    elif score <= 5:

        difficulty = "easy"

        difficulty_instruction = """
Ask a foundational question testing basic understanding.
"""

    else:

        difficulty = "medium"

        difficulty_instruction = """
Ask a practical medium-difficulty interview question.
"""


    prompt = f"""
You are an adaptive senior technical interviewer.

Previous Question:

{previous_question}

Candidate Answer:

{previous_answer}

Previous Score:

{score}/10

Previous Weaknesses:

{weaknesses}

NEXT TOPIC:

{next_topic}

DIFFICULTY:

{difficulty}

{difficulty_instruction}

Rules:

- Ask exactly ONE question.
- Focus strictly on the next topic.
- Do not give the answer.
- Do not explain anything.
- Do not number the question.
- Return only the question text.
"""


    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior "
                        "technical interviewer."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4
        )

    except Exception as error:

        print(
            "❌ ADAPTIVE GROQ ERROR:",
            repr(error)
        )

        raise ValueError(
            f"Adaptive question generation failed: "
            f"{error}"
        ) from error


    question = (
        response
        .choices[0]
        .message
        .content
    )


    if question is None:

        raise ValueError(
            "Groq returned None for "
            "adaptive question."
        )


    if not question.strip():

        raise ValueError(
            "Groq returned an empty "
            "adaptive question."
        )


    return question.strip()
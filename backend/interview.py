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


ROLE_TOPICS = {
    "AI Engineer": [
        "resume introduction",
        "machine learning",
        "LLM and AI engineering",
        "RAG and retrieval",
        "AI evaluation",
        "backend and APIs",
        "deployment and production",
        "AI system design",
        "project experience",
        "behavioral",
    ],
    "ML Engineer": [
        "resume introduction",
        "machine learning",
        "feature engineering",
        "model evaluation",
        "ML pipelines",
        "MLOps",
        "deployment and production",
        "system design",
        "project experience",
        "behavioral",
    ],
    "Data Scientist": [
        "resume introduction",
        "statistics",
        "machine learning",
        "data preprocessing",
        "feature engineering",
        "model evaluation",
        "experimentation",
        "business problem solving",
        "project experience",
        "behavioral",
    ],
    "Data Analyst": [
        "resume introduction",
        "SQL",
        "data cleaning",
        "statistics",
        "data visualization",
        "business analytics",
        "dashboarding",
        "case study",
        "project experience",
        "behavioral",
    ],
    "Backend Engineer": [
        "resume introduction",
        "data structures and algorithms",
        "backend development",
        "APIs",
        "databases",
        "authentication and security",
        "scalability",
        "deployment and production",
        "system design",
        "behavioral",
    ],
}


def generate_questions(
    resume_text: str,
    target_role: str,
) -> list[dict]:

    if target_role not in ROLE_TOPICS:
        raise ValueError(
            f"Unsupported target role: {target_role}"
        )

    interview_topics = ROLE_TOPICS[target_role]

    prompt = f"""
You are a senior technical interviewer hiring for the role of:

{target_role}

Generate exactly 10 personalized interview questions
based on the candidate resume and the target role.

The interview must contain exactly one question
for each of these role-specific topics:

{json.dumps(interview_topics)}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "questions": [
        {{
            "topic": "topic name",
            "question": "Question text"
        }}
    ]
}}

Rules:

- Return exactly 10 question objects.
- Use the exact topics provided.
- Generate one question per topic in the same order.
- Make every question relevant to the {target_role} role.
- Personalize questions using the candidate resume.
- If the resume does not mention a topic directly, ask a realistic
  role-level question that tests the candidate's understanding.
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
                        f"You are a senior {target_role} interviewer. "
                        "Always return valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
            response_format={
                "type": "json_object"
            },
        )

    except Exception as error:
        print(
            "❌ GROQ API ERROR:",
            repr(error),
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
        print("❌ JSON PARSING FAILED")
        print("RAW RESPONSE:")
        print(repr(raw_response))

        raise ValueError(
            "Groq returned invalid JSON. "
            f"JSON error: {error}"
        ) from error

    questions = parsed_response.get(
        "questions"
    )

    if not isinstance(
        questions,
        list,
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
        interview_topics
    ):
        question_data = questions[index]

        if not isinstance(
            question_data,
            dict,
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
                "question": question.strip(),
            }
        )

    return validated_questions


def generate_adaptive_question(
    previous_question: str,
    previous_answer: str,
    score: float,
    weaknesses: list[str],
    next_topic: str,
    target_role: str,
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
You are an adaptive senior technical interviewer
hiring for the role of {target_role}.

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
- Make the question appropriate for a {target_role} interview.
- Adapt difficulty using the previous performance.
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
                        f"You are a senior {target_role} "
                        "technical interviewer."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.4,
        )

    except Exception as error:
        print(
            "❌ ADAPTIVE GROQ ERROR:",
            repr(error),
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

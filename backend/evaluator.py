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


def evaluate_answer(
    question: str,
    answer: str
) -> dict:
    """
    Evaluate a candidate's interview answer
    across multiple interview dimensions.
    """

    prompt = f"""
You are a senior technical interviewer.

Evaluate the candidate's interview answer fairly
and consistently.

Interview Question:

{question}

Candidate Answer:

{answer}

Evaluate the candidate across these dimensions:

1. Technical Accuracy
- correctness of technical concepts
- correct terminology
- absence of factual errors

2. Communication
- clarity
- structure
- ability to explain concepts simply

3. Depth
- detailed understanding
- trade-offs
- reasoning
- practical knowledge

4. Relevance
- how directly the answer addresses the question

Return ONLY valid JSON.

Use exactly this JSON structure:

{{
    "overall_score": 8.2,
    "technical_accuracy": 8.5,
    "communication": 7.5,
    "depth": 7.0,
    "relevance": 9.0,
    "strengths": [
        "Strength one",
        "Strength two"
    ],
    "weaknesses": [
        "Weakness one",
        "Weakness two"
    ],
    "topics_to_improve": [
        "Topic one",
        "Topic two"
    ],
    "improved_answer": "Write an improved interview answer."
}}

Rules:

- All scores must be numbers between 0 and 10.
- Return valid JSON only.
- Do not use markdown.
- Do not use code fences.
- Do not include additional explanation.
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior technical interviewer. "
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
            "EVALUATOR GROQ API ERROR:",
            repr(error)
        )

        raise ValueError(
            f"Groq evaluation API failed: {error}"
        ) from error


    result = (
        response
        .choices[0]
        .message
        .content
    )


    print(
        "RAW EVALUATOR RESPONSE:"
    )

    print(
        repr(result)
    )


    if result is None:

        raise ValueError(
            "Groq returned None during evaluation."
        )


    if not result.strip():

        raise ValueError(
            "Groq returned an empty evaluation response."
        )


    try:

        feedback = json.loads(
            result
        )

    except json.JSONDecodeError as error:

        print(
            "EVALUATOR JSON PARSING FAILED"
        )

        print(
            "RAW RESPONSE:"
        )

        print(
            repr(result)
        )

        raise ValueError(
            "Groq returned invalid evaluation JSON. "
            f"JSON error: {error}"
        ) from error


    required_keys = {
        "overall_score",
        "technical_accuracy",
        "communication",
        "depth",
        "relevance",
        "strengths",
        "weaknesses",
        "topics_to_improve",
        "improved_answer"
    }


    missing_keys = (
        required_keys - feedback.keys()
    )


    if missing_keys:

        raise ValueError(
            f"Missing evaluation fields: "
            f"{missing_keys}"
        )


    score_keys = [
        "overall_score",
        "technical_accuracy",
        "communication",
        "depth",
        "relevance"
    ]


    for key in score_keys:

        try:

            score = float(
                feedback[key]
            )

        except (
            TypeError,
            ValueError
        ) as error:

            raise ValueError(
                f"{key} must be a number."
            ) from error


        if not 0 <= score <= 10:

            raise ValueError(
                f"{key} must be between 0 and 10."
            )


        feedback[key] = score


    if not isinstance(
        feedback["strengths"],
        list
    ):

        raise ValueError(
            "strengths must be a list."
        )


    if not isinstance(
        feedback["weaknesses"],
        list
    ):

        raise ValueError(
            "weaknesses must be a list."
        )


    if not isinstance(
        feedback["topics_to_improve"],
        list
    ):

        raise ValueError(
            "topics_to_improve must be a list."
        )


    return feedback
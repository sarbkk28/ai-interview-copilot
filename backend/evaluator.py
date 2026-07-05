import json
import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
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

Use exactly this structure:

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

All scores must be numbers between 0 and 10.

Scoring guide:

0-3:
Poor or incorrect.

4-5:
Basic understanding with major gaps.

6-7:
Good but lacks depth.

8-9:
Strong interview answer.

10:
Exceptional expert-level answer.

Return JSON only.
Do not use markdown.
Do not include additional explanation.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    result = response.choices[0].message.content

    feedback = json.loads(result)

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
            f"Missing evaluation fields: {missing_keys}"
        )

    return feedback
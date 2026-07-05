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
    Evaluate a candidate's interview answer.
    """

    prompt = f"""
You are a senior technical interviewer.

Evaluate the candidate's interview answer fairly.

Interview Question:

{question}

Candidate Answer:

{answer}

Evaluate the answer based on:

1. Technical correctness
2. Relevance
3. Depth of explanation
4. Communication clarity

Return ONLY valid JSON.

Use exactly this structure:

{{
    "score": 8.5,
    "strengths": [
        "Strength one",
        "Strength two"
    ],
    "weaknesses": [
        "Weakness one",
        "Weakness two"
    ],
    "improved_answer": "Write an improved interview answer."
}}

Scoring rules:

0-3:
Incorrect or extremely weak answer.

4-5:
Basic understanding but major concepts are missing.

6-7:
Good answer but lacks depth.

8-9:
Strong and technically accurate answer.

10:
Exceptional expert-level answer.

Return JSON only.
Do not include markdown.
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
        temperature=0.3
    )

    result = response.choices[0].message.content

    return json.loads(result)
import json
import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing from .env")

client = Groq(api_key=api_key)


def generate_followup_decision(
    question: str,
    answer: str,
    score: float,
    weaknesses: list[str],
    topic: str,
) -> dict:
    """
    Decide whether one targeted follow-up question is useful.

    Returns:
    {
        "ask_followup": bool,
        "reason": str,
        "followup_question": str
    }
    """

    prompt = f"""
You are a senior technical interviewer conducting a realistic interview.

TOPIC:
{topic}

CURRENT QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

ANSWER SCORE:
{score}/10

IDENTIFIED WEAKNESSES:
{json.dumps(weaknesses)}

Decide whether asking ONE immediate follow-up question would make the
interview more useful and realistic.

Ask a follow-up only when the candidate:
- mentions a technical tool, architecture, model, algorithm, metric,
  framework, research choice, or design decision worth probing;
- makes an important claim that needs justification;
- gives a vague or shallow explanation where one targeted probe can
  reveal actual understanding;
- misses a trade-off, failure mode, scalability concern, or practical
  detail directly connected to the answer.

Do NOT ask a follow-up merely because the answer is imperfect.
Do NOT change to a different topic.
Do NOT repeat the original question.
Do NOT ask multiple questions.
The follow-up must directly reference the candidate's answer.

Return ONLY valid JSON using exactly this structure:

{{
    "ask_followup": true,
    "reason": "Short internal reason for the decision.",
    "followup_question": "One targeted interview question."
}}

If no follow-up is useful, return:

{{
    "ask_followup": false,
    "reason": "Short internal reason for the decision.",
    "followup_question": ""
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a realistic senior technical interviewer. "
                        "Always return valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
    except Exception as error:
        print("FOLLOW-UP GROQ ERROR:", repr(error))
        raise ValueError(
            f"Follow-up decision generation failed: {error}"
        ) from error

    raw_response = response.choices[0].message.content

    if raw_response is None or not raw_response.strip():
        raise ValueError("Groq returned an empty follow-up decision.")

    try:
        result = json.loads(raw_response)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Groq returned invalid follow-up JSON: {error}"
        ) from error

    ask_followup = result.get("ask_followup")
    reason = result.get("reason", "")
    followup_question = result.get("followup_question", "")

    if not isinstance(ask_followup, bool):
        raise ValueError("ask_followup must be a boolean.")

    if not isinstance(reason, str):
        reason = str(reason)

    if not isinstance(followup_question, str):
        raise ValueError("followup_question must be a string.")

    followup_question = followup_question.strip()

    if ask_followup and not followup_question:
        raise ValueError(
            "Follow-up decision was true but the question was empty."
        )

    return {
        "ask_followup": ask_followup,
        "reason": reason.strip(),
        "followup_question": followup_question,
    }
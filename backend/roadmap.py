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


def generate_prep_roadmap(
    interview_history: list[dict],
) -> dict:

    if not interview_history:

        raise ValueError(
            "Interview history is empty."
        )


    history_json = json.dumps(
        interview_history,
        indent=2,
    )


    prompt = f"""
You are a senior technical interview coach.

Analyze the candidate's previous interview performance.

The interview history contains:

- interview topics
- interview questions
- candidate answers
- overall scores
- technical accuracy scores
- communication scores
- depth scores
- relevance scores
- weaknesses
- topics to improve

INTERVIEW HISTORY:

{history_json}

Generate a personalized technical interview preparation roadmap.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "readiness_level": "Intermediate",

    "readiness_summary": "Short explanation of the candidate's current interview readiness.",

    "priority_areas": [
        {{
            "priority": 1,
            "topic": "System Design",
            "reason": "The candidate repeatedly showed limited depth in scalability concepts.",
            "focus_topics": [
                "Load balancing",
                "Caching",
                "Database scaling"
            ]
        }},
        {{
            "priority": 2,
            "topic": "Backend APIs",
            "reason": "The candidate needs stronger practical API knowledge.",
            "focus_topics": [
                "REST API design",
                "HTTP status codes",
                "API authentication"
            ]
        }},
        {{
            "priority": 3,
            "topic": "Machine Learning",
            "reason": "The candidate needs deeper ML reasoning.",
            "focus_topics": [
                "Bias variance tradeoff",
                "Model evaluation",
                "Feature engineering"
            ]
        }}
    ],

    "seven_day_plan": [
        {{
            "day": 1,
            "title": "System Design Fundamentals",
            "topics": [
                "Scalability",
                "Load balancing"
            ],
            "practice_task": "Design a scalable URL shortener.",
            "estimated_hours": 2
        }},
        {{
            "day": 2,
            "title": "Backend API Fundamentals",
            "topics": [
                "REST APIs",
                "HTTP methods"
            ],
            "practice_task": "Explain the architecture of one of your FastAPI projects.",
            "estimated_hours": 2
        }}
    ],

    "interview_strategy": [
        "Use structured answers.",
        "Explain technical trade-offs.",
        "Use examples from personal projects."
    ],

    "final_recommendation": "Short personalized recommendation."
}}

Rules:

- Return exactly 3 priority areas.
- Return exactly 7 objects in seven_day_plan.
- Days must be numbered 1 to 7.
- Base recommendations on the interview history.
- Do not invent weaknesses unrelated to the interview history.
- Make the plan practical.
- Include coding, technical revision, and interview practice when relevant.
- Personalize practice tasks using the candidate's demonstrated topics when possible.
- estimated_hours must be a number.
- Return JSON only.
- Do not use markdown.
- Do not use code fences.
"""


    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior technical "
                        "interview coach. "
                        "Always return valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.3,
            response_format={
                "type": "json_object"
            },
        )


    except Exception as error:

        print(
            "ROADMAP GROQ ERROR:",
            repr(error),
        )


        raise ValueError(
            f"Roadmap generation failed: {error}"
        ) from error


    raw_response = (
        response
        .choices[0]
        .message
        .content
    )


    print(
        "RAW ROADMAP RESPONSE:"
    )


    print(
        repr(raw_response)
    )


    if raw_response is None:

        raise ValueError(
            "Groq returned None "
            "for the roadmap."
        )


    if not raw_response.strip():

        raise ValueError(
            "Groq returned an empty roadmap."
        )


    try:

        roadmap = json.loads(
            raw_response
        )


    except json.JSONDecodeError as error:

        print(
            "ROADMAP JSON ERROR:",
            repr(error),
        )


        print(
            "RAW RESPONSE:",
            repr(raw_response),
        )


        raise ValueError(
            "Groq returned invalid roadmap JSON."
        ) from error


    required_keys = {
        "readiness_level",
        "readiness_summary",
        "priority_areas",
        "seven_day_plan",
        "interview_strategy",
        "final_recommendation",
    }


    missing_keys = (
        required_keys
        - roadmap.keys()
    )


    if missing_keys:

        raise ValueError(
            f"Roadmap missing fields: "
            f"{missing_keys}"
        )


    priority_areas = roadmap[
        "priority_areas"
    ]


    seven_day_plan = roadmap[
        "seven_day_plan"
    ]


    if not isinstance(
        priority_areas,
        list,
    ):

        raise ValueError(
            "priority_areas must be a list."
        )


    if len(priority_areas) != 3:

        raise ValueError(
            "Expected exactly 3 priority areas."
        )


    if not isinstance(
        seven_day_plan,
        list,
    ):

        raise ValueError(
            "seven_day_plan must be a list."
        )


    if len(seven_day_plan) != 7:

        raise ValueError(
            "Expected exactly 7 roadmap days."
        )


    validated_days = []


    for index, day_data in enumerate(
        seven_day_plan,
        start=1,
    ):

        if not isinstance(
            day_data,
            dict,
        ):

            raise ValueError(
                f"Day {index} has "
                "an invalid structure."
            )


        day_data["day"] = index


        validated_days.append(
            day_data
        )


    roadmap[
        "seven_day_plan"
    ] = validated_days


    return roadmap
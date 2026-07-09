import json

from backend.database import get_database_connection


def create_interview(
    resume_filename: str
) -> int:
    """
    Create a new interview session.
    """

    connection = get_database_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO interviews (
            resume_filename
        )
        VALUES (?)
        """,
        (
            resume_filename,
        )
    )


    connection.commit()


    interview_id = cursor.lastrowid


    connection.close()


    return interview_id


def save_interview_answer(
    interview_id: int,
    question_number: int,
    topic: str,
    question: str,
    answer: str,
    feedback: dict
):
    """
    Save one interview answer and its evaluation.
    """

    connection = get_database_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO interview_answers (
            interview_id,
            question_number,
            topic,
            question,
            answer,
            overall_score,
            technical_accuracy,
            communication,
            depth,
            relevance,
            strengths,
            weaknesses,
            topics_to_improve,
            improved_answer
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            interview_id,
            question_number,
            topic,
            question,
            answer,
            feedback["overall_score"],
            feedback["technical_accuracy"],
            feedback["communication"],
            feedback["depth"],
            feedback["relevance"],
            json.dumps(
                feedback.get(
                    "strengths",
                    []
                )
            ),
            json.dumps(
                feedback.get(
                    "weaknesses",
                    []
                )
            ),
            json.dumps(
                feedback.get(
                    "topics_to_improve",
                    []
                )
            ),
            feedback.get(
                "improved_answer",
                ""
            )
        )
    )


    connection.commit()

    connection.close()


def complete_interview(
    interview_id: int
):
    """
    Mark an interview as completed and
    calculate its final average score.
    """

    connection = get_database_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT AVG(overall_score)
        AS average_score
        FROM interview_answers
        WHERE interview_id = ?
        """,
        (
            interview_id,
        )
    )


    result = cursor.fetchone()


    average_score = (
        result["average_score"]
        if result["average_score"] is not None
        else 0.0
    )


    cursor.execute(
        """
        UPDATE interviews

        SET
            completed = 1,
            overall_score = ?

        WHERE id = ?
        """,
        (
            average_score,
            interview_id
        )
    )


    connection.commit()

    connection.close()


    return average_score


def get_all_interviews():
    """
    Return all interview sessions.
    """

    connection = get_database_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT
            id,
            resume_filename,
            created_at,
            completed,
            overall_score

        FROM interviews

        ORDER BY created_at DESC
        """
    )


    interviews = cursor.fetchall()


    connection.close()


    return [
        dict(interview)
        for interview in interviews
    ]


def get_interview_answers(
    interview_id: int
):
    """
    Return all answers for an interview.
    """

    connection = get_database_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *

        FROM interview_answers

        WHERE interview_id = ?

        ORDER BY question_number
        """,
        (
            interview_id,
        )
    )


    answers = cursor.fetchall()


    connection.close()


    results = []


    for answer in answers:

        answer_data = dict(answer)


        answer_data["strengths"] = json.loads(
            answer_data["strengths"]
            or "[]"
        )


        answer_data["weaknesses"] = json.loads(
            answer_data["weaknesses"]
            or "[]"
        )


        answer_data[
            "topics_to_improve"
        ] = json.loads(
            answer_data[
                "topics_to_improve"
            ]
            or "[]"
        )


        results.append(
            answer_data
        )


    return results
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


def calculate_average(values):

    if not values:
        return 0.0

    return sum(values) / len(values)


def generate_interview_report(
    interview_id: int,
    answers: list[dict],
) -> bytes:

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=15,
        spaceBefore=12,
        spaceAfter=10,
    )

    question_style = ParagraphStyle(
        "QuestionStyle",
        parent=styles["Heading3"],
        fontSize=12,
        spaceAfter=8,
    )

    body_style = styles["BodyText"]

    body_style.leading = 16

    story = []

    story.append(
        Paragraph(
            "AI Interview Copilot",
            title_style,
        )
    )

    story.append(
        Paragraph(
            f"Interview Performance Report #{interview_id}",
            styles["Heading2"],
        )
    )

    story.append(
        Spacer(
            1,
            0.25 * inch,
        )
    )

    if not answers:

        story.append(
            Paragraph(
                "No interview answers were found.",
                body_style,
            )
        )

        document.build(story)

        pdf_data = buffer.getvalue()

        buffer.close()

        return pdf_data

    overall_scores = [
        float(answer["overall_score"])
        for answer in answers
    ]

    technical_scores = [
        float(answer["technical_accuracy"])
        for answer in answers
    ]

    communication_scores = [
        float(answer["communication"])
        for answer in answers
    ]

    depth_scores = [
        float(answer["depth"])
        for answer in answers
    ]

    relevance_scores = [
        float(answer["relevance"])
        for answer in answers
    ]

    average_overall = calculate_average(
        overall_scores
    )

    average_technical = calculate_average(
        technical_scores
    )

    average_communication = calculate_average(
        communication_scores
    )

    average_depth = calculate_average(
        depth_scores
    )

    average_relevance = calculate_average(
        relevance_scores
    )

    story.append(
        Paragraph(
            "Performance Summary",
            heading_style,
        )
    )

    summary_data = [
        [
            "Metric",
            "Score",
        ],
        [
            "Overall Score",
            f"{average_overall:.1f}/10",
        ],
        [
            "Technical Accuracy",
            f"{average_technical:.1f}/10",
        ],
        [
            "Communication",
            f"{average_communication:.1f}/10",
        ],
        [
            "Depth",
            f"{average_depth:.1f}/10",
        ],
        [
            "Relevance",
            f"{average_relevance:.1f}/10",
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            250,
            100,
        ],
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#2F4F4F"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.grey,
                ),
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.whitesmoke,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(
        summary_table
    )

    story.append(
        Spacer(
            1,
            0.3 * inch,
        )
    )

    skill_scores = {
        "Technical Accuracy": average_technical,
        "Communication": average_communication,
        "Depth": average_depth,
        "Relevance": average_relevance,
    }

    strongest_skill = max(
        skill_scores,
        key=skill_scores.get,
    )

    weakest_skill = min(
        skill_scores,
        key=skill_scores.get,
    )

    story.append(
        Paragraph(
            "Interview Insights",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            (
                f"<b>Strongest Skill:</b> "
                f"{strongest_skill} "
                f"({skill_scores[strongest_skill]:.1f}/10)"
            ),
            body_style,
        )
    )

    story.append(
        Spacer(
            1,
            8,
        )
    )

    story.append(
        Paragraph(
            (
                f"<b>Primary Focus Area:</b> "
                f"{weakest_skill} "
                f"({skill_scores[weakest_skill]:.1f}/10)"
            ),
            body_style,
        )
    )

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "Detailed Interview Review",
            heading_style,
        )
    )

    for answer in answers:

        question_number = answer[
            "question_number"
        ]

        topic = (
            answer["topic"]
            .replace("_", " ")
            .title()
        )

        score = float(
            answer["overall_score"]
        )

        story.append(
            Paragraph(
                (
                    f"Question {question_number}: "
                    f"{topic}"
                ),
                question_style,
            )
        )

        story.append(
            Paragraph(
                (
                    f"<b>Score:</b> "
                    f"{score:.1f}/10"
                ),
                body_style,
            )
        )

        story.append(
            Spacer(
                1,
                6,
            )
        )

        story.append(
            Paragraph(
                "<b>Question</b>",
                body_style,
            )
        )

        story.append(
            Paragraph(
                str(answer["question"]),
                body_style,
            )
        )

        story.append(
            Spacer(
                1,
                8,
            )
        )

        story.append(
            Paragraph(
                "<b>Candidate Answer</b>",
                body_style,
            )
        )

        story.append(
            Paragraph(
                str(answer["answer"]),
                body_style,
            )
        )

        story.append(
            Spacer(
                1,
                8,
            )
        )

        strengths = answer.get(
            "strengths",
            [],
        )

        story.append(
            Paragraph(
                "<b>Strengths</b>",
                body_style,
            )
        )

        if strengths:

            for strength in strengths:

                story.append(
                    Paragraph(
                        f"- {strength}",
                        body_style,
                    )
                )

        else:

            story.append(
                Paragraph(
                    "No strengths recorded.",
                    body_style,
                )
            )

        story.append(
            Spacer(
                1,
                8,
            )
        )

        weaknesses = answer.get(
            "weaknesses",
            [],
        )

        story.append(
            Paragraph(
                "<b>Areas to Improve</b>",
                body_style,
            )
        )

        if weaknesses:

            for weakness in weaknesses:

                story.append(
                    Paragraph(
                        f"- {weakness}",
                        body_style,
                    )
                )

        else:

            story.append(
                Paragraph(
                    "No weaknesses recorded.",
                    body_style,
                )
            )

        story.append(
            Spacer(
                1,
                8,
            )
        )

        topics = answer.get(
            "topics_to_improve",
            [],
        )

        story.append(
            Paragraph(
                "<b>Topics to Improve</b>",
                body_style,
            )
        )

        if topics:

            for topic_to_improve in topics:

                story.append(
                    Paragraph(
                        f"- {topic_to_improve}",
                        body_style,
                    )
                )

        else:

            story.append(
                Paragraph(
                    "No topics recorded.",
                    body_style,
                )
            )

        story.append(
            Spacer(
                1,
                8,
            )
        )

        story.append(
            Paragraph(
                "<b>Improved Answer</b>",
                body_style,
            )
        )

        story.append(
            Paragraph(
                str(
                    answer.get(
                        "improved_answer",
                        "No improved answer recorded.",
                    )
                ),
                body_style,
            )
        )

        story.append(
            Spacer(
                1,
                20,
            )
        )

    document.build(
        story
    )

    pdf_data = buffer.getvalue()

    buffer.close()

    return pdf_data
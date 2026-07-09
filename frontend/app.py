import pandas as pd
import requests
import streamlit as st


API_URL = "http://127.0.0.1:8001"


st.set_page_config(
    page_title="AI Interview Copilot",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------


def initialize_session_state():
    """
    Initialize Streamlit interview state.
    """

    default_values = {
        "questions": [],
        "current_question": 0,
        "history": [],
        "feedback": None,
        "interview_started": False
    }

    for key, value in default_values.items():

        if key not in st.session_state:

            st.session_state[key] = value


def reset_interview():
    """
    Reset complete interview session.
    """

    st.session_state.questions = []

    st.session_state.current_question = 0

    st.session_state.history = []

    st.session_state.feedback = None

    st.session_state.interview_started = False


def calculate_average(scores):
    """
    Calculate average score.
    """

    if not scores:

        return 0.0

    return sum(scores) / len(scores)


initialize_session_state()


# --------------------------------------------------
# HEADER
# --------------------------------------------------


st.title(
    "🤖 AI Interview Copilot"
)


st.caption(
    "Adaptive AI-powered mock interviews "
    "personalized using your resume."
)


# --------------------------------------------------
# RESUME UPLOAD
# --------------------------------------------------


if not st.session_state.interview_started:

    st.subheader(
        "📄 Start Your Interview"
    )


    uploaded_file = st.file_uploader(
        "Upload your Resume",
        type=[
            "pdf",
            "docx"
        ]
    )


    if uploaded_file is not None:

        if st.button(
            "🚀 Start Interview",
            type="primary"
        ):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file,
                    uploaded_file.type
                )
            }


            with st.spinner(
                "Analyzing your resume and "
                "preparing personalized questions..."
            ):

                try:

                    response = requests.post(
                        f"{API_URL}/upload_resume",
                        files=files,
                        timeout=120
                    )


                except requests.RequestException as error:

                    st.error(
                        "Unable to connect to backend."
                    )

                    st.write(
                        error
                    )

                    st.stop()


            if response.status_code == 200:

                data = response.json()


                questions = data.get(
                    "questions",
                    []
                )


                if not questions:

                    st.error(
                        "Backend returned no "
                        "interview questions."
                    )

                    st.stop()


                st.session_state.questions = (
                    questions
                )

                st.session_state.current_question = 0

                st.session_state.history = []

                st.session_state.feedback = None

                st.session_state.interview_started = True


                st.rerun()


            else:

                st.error(
                    "Failed to prepare interview."
                )

                st.write(
                    response.text
                )


# --------------------------------------------------
# INTERVIEW MODE
# --------------------------------------------------


else:

    questions = (
        st.session_state.questions
    )


    current_index = (
        st.session_state.current_question
    )


    total_questions = len(
        questions
    )


    # --------------------------------------------------
    # ACTIVE INTERVIEW
    # --------------------------------------------------


    if current_index < total_questions:

        current_question_data = (
            questions[current_index]
        )


        if not isinstance(
            current_question_data,
            dict
        ):

            st.error(
                "Invalid question format "
                "received from backend."
            )

            st.write(
                current_question_data
            )

            st.stop()


        current_question = (
            current_question_data.get(
                "question",
                ""
            )
        )


        current_topic = (
            current_question_data.get(
                "topic",
                "general"
            )
        )


        if not isinstance(
            current_question,
            str
        ):

            st.error(
                "Question text must "
                "be a string."
            )

            st.write(
                current_question_data
            )

            st.stop()


        if not current_question.strip():

            st.error(
                "Question text is empty."
            )

            st.stop()


        # --------------------------------------------------
        # PROGRESS
        # --------------------------------------------------


        progress = (
            current_index
            / total_questions
        )


        st.progress(
            progress
        )


        st.caption(
            f"Question "
            f"{current_index + 1} "
            f"of {total_questions}"
        )


        st.caption(
            f"🎯 Interview Topic: "
            f"{current_topic.title()}"
        )


        st.subheader(
            f"🎤 {current_question}"
        )


        # --------------------------------------------------
        # ANSWER INPUT
        # --------------------------------------------------


        answer = st.text_area(
            "Your Answer",
            height=180,
            key=(
                f"answer_"
                f"{current_index}"
            ),
            placeholder=(
                "Type your interview "
                "answer here..."
            ),
            disabled=(
                st.session_state.feedback
                is not None
            )
        )


        # --------------------------------------------------
        # SUBMIT ANSWER
        # --------------------------------------------------


        if (
            st.session_state.feedback
            is None
        ):

            if st.button(
                "Submit Answer",
                type="primary"
            ):

                if not answer.strip():

                    st.warning(
                        "Please write an answer "
                        "before submitting."
                    )


                else:

                    evaluate_payload = {
                        "question": (
                            current_question
                        ),
                        "answer": answer
                    }


                    with st.spinner(
                        "AI interviewer is "
                        "evaluating your answer..."
                    ):

                        try:

                            response = requests.post(
                                f"{API_URL}/evaluate",
                                json=evaluate_payload,
                                timeout=120
                            )


                        except requests.RequestException as error:

                            st.error(
                                "Unable to evaluate answer."
                            )

                            st.write(
                                error
                            )

                            st.stop()


                    if (
                        response.status_code
                        == 200
                    ):

                        feedback = (
                            response.json()
                        )


                        st.session_state.feedback = (
                            feedback
                        )


                        st.session_state.history.append(
                            {
                                "topic": (
                                    current_topic
                                ),
                                "question": (
                                    current_question
                                ),
                                "answer": answer,
                                "feedback": feedback
                            }
                        )


                        st.rerun()


                    else:

                        st.error(
                            "Answer evaluation failed."
                        )

                        st.write(
                            response.text
                        )


        # --------------------------------------------------
        # FEEDBACK
        # --------------------------------------------------


        if (
            st.session_state.feedback
            is not None
        ):

            feedback = (
                st.session_state.feedback
            )


            score = float(
                feedback[
                    "overall_score"
                ]
            )


            st.divider()


            st.header(
                "📊 Interview Feedback"
            )


            # --------------------------------------------------
            # OVERALL SCORE
            # --------------------------------------------------


            st.metric(
                "⭐ Overall Score",
                f"{score:.1f}/10"
            )


            # --------------------------------------------------
            # SKILL SCORES
            # --------------------------------------------------


            col1, col2, col3, col4 = (
                st.columns(4)
            )


            with col1:

                technical_score = float(
                    feedback[
                        "technical_accuracy"
                    ]
                )


                st.metric(
                    "🎯 Technical Accuracy",
                    f"{technical_score:.1f}/10"
                )


            with col2:

                communication_score = float(
                    feedback[
                        "communication"
                    ]
                )


                st.metric(
                    "💬 Communication",
                    f"{communication_score:.1f}/10"
                )


            with col3:

                depth_score = float(
                    feedback["depth"]
                )


                st.metric(
                    "🧠 Depth",
                    f"{depth_score:.1f}/10"
                )


            with col4:

                relevance_score = float(
                    feedback["relevance"]
                )


                st.metric(
                    "📌 Relevance",
                    f"{relevance_score:.1f}/10"
                )


            # --------------------------------------------------
            # ADAPTIVE MESSAGE
            # --------------------------------------------------


            if score >= 8:

                st.success(
                    "🔥 Strong answer! "
                    "The next topic will use "
                    "a more challenging question."
                )


            elif score <= 5:

                st.warning(
                    "📚 The next topic will use "
                    "a foundational question."
                )


            else:

                st.info(
                    "👍 Good attempt. "
                    "The next topic will use "
                    "a medium-difficulty question."
                )


            # --------------------------------------------------
            # STRENGTHS
            # --------------------------------------------------


            st.subheader(
                "✅ Strengths"
            )


            for strength in feedback.get(
                "strengths",
                []
            ):

                st.success(
                    strength
                )


            # --------------------------------------------------
            # WEAKNESSES
            # --------------------------------------------------


            st.subheader(
                "⚠️ Areas to Improve"
            )


            for weakness in feedback.get(
                "weaknesses",
                []
            ):

                st.warning(
                    weakness
                )


            # --------------------------------------------------
            # TOPICS TO IMPROVE
            # --------------------------------------------------


            st.subheader(
                "📚 Topics to Improve"
            )


            topics_to_improve = (
                feedback.get(
                    "topics_to_improve",
                    []
                )
            )


            if topics_to_improve:

                for topic in topics_to_improve:

                    st.write(
                        f"• {topic}"
                    )


            else:

                st.write(
                    "No specific improvement "
                    "topics identified."
                )


            # --------------------------------------------------
            # IMPROVED ANSWER
            # --------------------------------------------------


            st.subheader(
                "💡 Improved Answer"
            )


            st.info(
                feedback.get(
                    "improved_answer",
                    (
                        "No improved "
                        "answer generated."
                    )
                )
            )


            # --------------------------------------------------
            # NEXT QUESTION
            # --------------------------------------------------


            if st.button(
                "Next Question ➡️",
                type="primary"
            ):

                last_interview = (
                    st.session_state.history[-1]
                )


                next_index = (
                    st.session_state.current_question
                    + 1
                )


                if next_index < total_questions:

                    next_question_data = (
                        st.session_state.questions[
                            next_index
                        ]
                    )


                    if not isinstance(
                        next_question_data,
                        dict
                    ):

                        st.error(
                            "Invalid next "
                            "question format."
                        )

                        st.write(
                            next_question_data
                        )

                        st.stop()


                    next_topic = (
                        next_question_data.get(
                            "topic",
                            "general"
                        )
                    )


                    adaptive_payload = {
                        "previous_question": (
                            last_interview[
                                "question"
                            ]
                        ),
                        "previous_answer": (
                            last_interview[
                                "answer"
                            ]
                        ),
                        "score": (
                            last_interview[
                                "feedback"
                            ][
                                "overall_score"
                            ]
                        ),
                        "weaknesses": (
                            last_interview[
                                "feedback"
                            ].get(
                                "weaknesses",
                                []
                            )
                        ),
                        "next_topic": next_topic
                    }


                    with st.spinner(
                        "AI interviewer is adapting "
                        f"the {next_topic.title()} "
                        "question..."
                    ):

                        try:

                            adaptive_response = (
                                requests.post(
                                    (
                                        f"{API_URL}"
                                        "/adaptive_question"
                                    ),
                                    json=adaptive_payload,
                                    timeout=120
                                )
                            )


                        except requests.RequestException as error:

                            st.error(
                                "Unable to generate "
                                "adaptive question."
                            )

                            st.write(
                                error
                            )

                            st.stop()


                    if (
                        adaptive_response.status_code
                        == 200
                    ):

                        adaptive_data = (
                            adaptive_response.json()
                        )


                        adaptive_question = (
                            adaptive_data.get(
                                "question",
                                ""
                            )
                        )


                        if not isinstance(
                            adaptive_question,
                            str
                        ):

                            st.error(
                                "Adaptive question "
                                "must be a string."
                            )

                            st.write(
                                adaptive_data
                            )

                            st.stop()


                        if not adaptive_question.strip():

                            st.error(
                                "Adaptive question "
                                "is empty."
                            )

                            st.stop()


                        st.session_state.questions[
                            next_index
                        ][
                            "question"
                        ] = adaptive_question


                    else:

                        st.error(
                            "Adaptive question "
                            "generation failed."
                        )

                        st.write(
                            adaptive_response.text
                        )

                        st.stop()


                st.session_state.current_question += 1

                st.session_state.feedback = None


                st.rerun()


    # --------------------------------------------------
    # INTERVIEW COMPLETE
    # --------------------------------------------------


    else:

        st.success(
            "🎉 Interview Completed!"
        )


        st.header(
            "📊 Interview Analytics Dashboard"
        )


        history = (
            st.session_state.history
        )


        if not history:

            st.warning(
                "No interview history found."
            )


            if st.button(
                "🔄 Start New Interview"
            ):

                reset_interview()

                st.rerun()


            st.stop()


        # --------------------------------------------------
        # SCORE COLLECTION
        # --------------------------------------------------


        overall_scores = [
            float(
                item["feedback"][
                    "overall_score"
                ]
            )
            for item in history
        ]


        technical_scores = [
            float(
                item["feedback"][
                    "technical_accuracy"
                ]
            )
            for item in history
        ]


        communication_scores = [
            float(
                item["feedback"][
                    "communication"
                ]
            )
            for item in history
        ]


        depth_scores = [
            float(
                item["feedback"]["depth"]
            )
            for item in history
        ]


        relevance_scores = [
            float(
                item["feedback"]["relevance"]
            )
            for item in history
        ]


        # --------------------------------------------------
        # AVERAGES
        # --------------------------------------------------


        average_overall = (
            calculate_average(
                overall_scores
            )
        )


        average_technical = (
            calculate_average(
                technical_scores
            )
        )


        average_communication = (
            calculate_average(
                communication_scores
            )
        )


        average_depth = (
            calculate_average(
                depth_scores
            )
        )


        average_relevance = (
            calculate_average(
                relevance_scores
            )
        )


        # --------------------------------------------------
        # OVERALL PERFORMANCE
        # --------------------------------------------------


        st.metric(
            "⭐ Overall Interview Score",
            f"{average_overall:.1f}/10"
        )


        st.progress(
            min(
                average_overall / 10,
                1.0
            )
        )


        # --------------------------------------------------
        # PERFORMANCE TREND CHART
        # --------------------------------------------------


        st.subheader(
            "📈 Interview Performance Trend"
        )


        trend_data = pd.DataFrame(
            {
                "Question": [
                    f"Q{index}"
                    for index in range(
                        1,
                        len(overall_scores) + 1
                    )
                ],
                "Score": overall_scores
            }
        )


        trend_data = trend_data.set_index(
            "Question"
        )


        st.line_chart(
            trend_data
        )


        # --------------------------------------------------
        # PERFORMANCE CHANGE
        # --------------------------------------------------


        if len(overall_scores) >= 2:

            score_change = (
                overall_scores[-1]
                - overall_scores[0]
            )


            if score_change > 0:

                st.success(
                    f"📈 Your performance improved by "
                    f"{score_change:.1f} points "
                    f"from Question 1 to "
                    f"Question {len(overall_scores)}."
                )


            elif score_change < 0:

                st.warning(
                    f"📉 Your score decreased by "
                    f"{abs(score_change):.1f} points "
                    f"during the interview."
                )


            else:

                st.info(
                    "Your interview performance "
                    "remained consistent."
                )


        # --------------------------------------------------
        # SKILL-WISE PERFORMANCE
        # --------------------------------------------------


        st.subheader(
            "🎯 Skill-wise Performance"
        )


        col1, col2 = (
            st.columns(2)
        )


        with col1:

            st.metric(
                "🎯 Technical Accuracy",
                f"{average_technical:.1f}/10"
            )


            st.progress(
                min(
                    average_technical / 10,
                    1.0
                )
            )


            st.metric(
                "🧠 Depth",
                f"{average_depth:.1f}/10"
            )


            st.progress(
                min(
                    average_depth / 10,
                    1.0
                )
            )


        with col2:

            st.metric(
                "💬 Communication",
                f"{average_communication:.1f}/10"
            )


            st.progress(
                min(
                    average_communication / 10,
                    1.0
                )
            )


            st.metric(
                "📌 Relevance",
                f"{average_relevance:.1f}/10"
            )


            st.progress(
                min(
                    average_relevance / 10,
                    1.0
                )
            )


        # --------------------------------------------------
        # SKILL COMPARISON CHART
        # --------------------------------------------------


        st.subheader(
            "📊 Skill Comparison"
        )


        skill_data = pd.DataFrame(
            {
                "Skill": [
                    "Technical Accuracy",
                    "Communication",
                    "Depth",
                    "Relevance"
                ],
                "Score": [
                    average_technical,
                    average_communication,
                    average_depth,
                    average_relevance
                ]
            }
        )


        skill_data = skill_data.set_index(
            "Skill"
        )


        st.bar_chart(
            skill_data
        )


        # --------------------------------------------------
        # STRONGEST AND WEAKEST SKILL
        # --------------------------------------------------


        skill_scores = {
            "Technical Accuracy": (
                average_technical
            ),
            "Communication": (
                average_communication
            ),
            "Depth": (
                average_depth
            ),
            "Relevance": (
                average_relevance
            )
        }


        strongest_skill = max(
            skill_scores,
            key=skill_scores.get
        )


        weakest_skill = min(
            skill_scores,
            key=skill_scores.get
        )


        col1, col2 = (
            st.columns(2)
        )


        with col1:

            st.success(
                f"🏆 Strongest Skill: "
                f"{strongest_skill} "
                f"("
                f"{skill_scores[strongest_skill]:.1f}"
                f"/10)"
            )


        with col2:

            st.warning(
                f"🎯 Focus Area: "
                f"{weakest_skill} "
                f"("
                f"{skill_scores[weakest_skill]:.1f}"
                f"/10)"
            )


        # --------------------------------------------------
        # TOPIC-WISE PERFORMANCE
        # --------------------------------------------------


        st.subheader(
            "🧩 Topic-wise Performance"
        )


        for item in history:

            topic = (
                item["topic"]
                .replace("_", " ")
                .title()
            )


            topic_score = float(
                item["feedback"][
                    "overall_score"
                ]
            )


            st.write(
                f"**{topic}**"
            )


            st.progress(
                min(
                    topic_score / 10,
                    1.0
                )
            )


            st.caption(
                f"Score: "
                f"{topic_score:.1f}/10"
            )


        # --------------------------------------------------
        # PRIORITY IMPROVEMENT TOPICS
        # --------------------------------------------------


        all_topics = []


        for item in history:

            all_topics.extend(
                item["feedback"].get(
                    "topics_to_improve",
                    []
                )
            )


        topic_counts = {}


        for topic in all_topics:

            normalized_topic = (
                topic
                .strip()
                .lower()
            )


            topic_counts[
                normalized_topic
            ] = (
                topic_counts.get(
                    normalized_topic,
                    0
                )
                + 1
            )


        sorted_topics = sorted(
            topic_counts.items(),
            key=lambda item: item[1],
            reverse=True
        )


        st.subheader(
            "📚 Priority Topics to Improve"
        )


        if sorted_topics:

            for topic, count in (
                sorted_topics[:5]
            ):

                st.warning(
                    f"{topic.title()} — "
                    f"identified "
                    f"{count} time(s)"
                )


        else:

            st.success(
                "No major recurring weak topics "
                "were identified."
            )


        # --------------------------------------------------
        # INTERVIEW RECOMMENDATION
        # --------------------------------------------------


        st.subheader(
            "💼 Interview Recommendation"
        )


        if average_overall >= 8.5:

            st.success(
                "🔥 Highly Recommended — "
                "Strong interview readiness."
            )


        elif average_overall >= 7:

            st.info(
                "👍 Recommended — "
                "Good performance with "
                "some areas to refine."
            )


        elif average_overall >= 5:

            st.warning(
                "📚 Needs Improvement — "
                "Strengthen identified "
                "weak topics."
            )


        else:

            st.error(
                "More Preparation Required — "
                "Focus on fundamentals "
                "before interviewing."
            )


        # --------------------------------------------------
        # INTERVIEW HISTORY
        # --------------------------------------------------


        st.divider()


        st.subheader(
            "📝 Interview History"
        )


        for index, item in enumerate(
            history,
            start=1
        ):

            score = float(
                item["feedback"][
                    "overall_score"
                ]
            )


            topic = (
                item["topic"]
                .replace("_", " ")
                .title()
            )


            with st.expander(
                f"Question {index} | "
                f"{topic} | "
                f"Score {score:.1f}/10"
            ):

                st.markdown(
                    "**Question**"
                )


                st.write(
                    item["question"]
                )


                st.markdown(
                    "**Your Answer**"
                )


                st.write(
                    item["answer"]
                )


                st.markdown(
                    "**Strengths**"
                )


                for strength in (
                    item["feedback"].get(
                        "strengths",
                        []
                    )
                ):

                    st.write(
                        f"✅ {strength}"
                    )


                st.markdown(
                    "**Areas to Improve**"
                )


                for weakness in (
                    item["feedback"].get(
                        "weaknesses",
                        []
                    )
                ):

                    st.write(
                        f"⚠️ {weakness}"
                    )


                st.markdown(
                    "**Improved Answer**"
                )


                st.info(
                    item["feedback"].get(
                        "improved_answer",
                        (
                            "No improved "
                            "answer generated."
                        )
                    )
                )


        # --------------------------------------------------
        # RESET
        # --------------------------------------------------


        st.divider()


        if st.button(
            "🔄 Start New Interview",
            type="primary"
        ):

            reset_interview()

            st.rerun()
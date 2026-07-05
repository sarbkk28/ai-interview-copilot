import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


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
    Reset the complete interview session.
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


st.title("🤖 AI Interview Copilot")

st.caption(
    "Adaptive AI-powered mock interviews "
    "personalized using your resume."
)


# --------------------------------------------------
# RESUME UPLOAD
# --------------------------------------------------


if not st.session_state.interview_started:

    st.subheader("📄 Start Your Interview")

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

                    st.write(error)

                    st.stop()

            if response.status_code == 200:

                data = response.json()

                st.session_state.questions = (
                    data["questions"]
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

                st.write(response.text)


# --------------------------------------------------
# INTERVIEW MODE
# --------------------------------------------------


else:

    questions = st.session_state.questions

    current_index = (
        st.session_state.current_question
    )

    total_questions = len(questions)


    # --------------------------------------------------
    # ACTIVE INTERVIEW
    # --------------------------------------------------


    if current_index < total_questions:

        current_question = (
            questions[current_index]
        )

        progress = (
            current_index / total_questions
        )

        st.progress(progress)

        st.caption(
            f"Question "
            f"{current_index + 1} "
            f"of {total_questions}"
        )

        st.subheader(
            f"🎤 {current_question}"
        )


        answer = st.text_area(
            "Your Answer",
            height=180,
            key=f"answer_{current_index}",
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


        if st.session_state.feedback is None:

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

                    with st.spinner(
                        "AI interviewer is "
                        "evaluating your answer..."
                    ):

                        try:

                            response = requests.post(
                                f"{API_URL}/evaluate",
                                json={
                                    "question": (
                                        current_question
                                    ),
                                    "answer": answer
                                },
                                timeout=120
                            )

                        except requests.RequestException as error:

                            st.error(
                                "Unable to evaluate answer."
                            )

                            st.write(error)

                            st.stop()


                    if response.status_code == 200:

                        feedback = response.json()

                        st.session_state.feedback = (
                            feedback
                        )

                        st.session_state.history.append(
                            {
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

                        st.write(response.text)


        # --------------------------------------------------
        # ANSWER FEEDBACK
        # --------------------------------------------------


        if st.session_state.feedback is not None:

            feedback = (
                st.session_state.feedback
            )

            score = float(
                feedback["overall_score"]
            )

            st.divider()

            st.header(
                "📊 Interview Feedback"
            )


            # Overall score

            st.metric(
                "⭐ Overall Score",
                f"{score:.1f}/10"
            )


            # Skill-wise scores

            col1, col2, col3, col4 = st.columns(4)


            with col1:

                st.metric(
                    "🎯 Technical Accuracy",
                    (
                        f"{float(feedback['technical_accuracy']):.1f}"
                        "/10"
                    )
                )


            with col2:

                st.metric(
                    "💬 Communication",
                    (
                        f"{float(feedback['communication']):.1f}"
                        "/10"
                    )
                )


            with col3:

                st.metric(
                    "🧠 Depth",
                    (
                        f"{float(feedback['depth']):.1f}"
                        "/10"
                    )
                )


            with col4:

                st.metric(
                    "📌 Relevance",
                    (
                        f"{float(feedback['relevance']):.1f}"
                        "/10"
                    )
                )


            # Adaptive difficulty message

            if score >= 8:

                st.success(
                    "🔥 Strong answer! "
                    "The next question will "
                    "be more challenging."
                )

            elif score <= 5:

                st.warning(
                    "📚 The next question will "
                    "focus on strengthening "
                    "your fundamentals."
                )

            else:

                st.info(
                    "👍 Good attempt. "
                    "The interviewer will "
                    "explore this topic further."
                )


            # Strengths

            st.subheader(
                "✅ Strengths"
            )

            for strength in feedback["strengths"]:

                st.success(strength)


            # Weaknesses

            st.subheader(
                "⚠️ Areas to Improve"
            )

            for weakness in feedback["weaknesses"]:

                st.warning(weakness)


            # Topics to improve

            st.subheader(
                "📚 Topics to Improve"
            )

            for topic in feedback["topics_to_improve"]:

                st.write(
                    f"• {topic}"
                )


            # Improved answer

            st.subheader(
                "💡 Improved Answer"
            )

            st.info(
                feedback["improved_answer"]
            )


            # --------------------------------------------------
            # ADAPTIVE NEXT QUESTION
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

                    with st.spinner(
                        "AI interviewer is adapting "
                        "the next question..."
                    ):

                        try:

                            adaptive_response = requests.post(
                                (
                                    f"{API_URL}"
                                    "/adaptive_question"
                                ),
                                json={
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
                                        ][
                                            "weaknesses"
                                        ]
                                    )
                                },
                                timeout=120
                            )

                        except requests.RequestException as error:

                            st.error(
                                "Unable to generate "
                                "adaptive question."
                            )

                            st.write(error)

                            st.stop()


                    if (
                        adaptive_response.status_code
                        == 200
                    ):

                        adaptive_question = (
                            adaptive_response.json()[
                                "question"
                            ]
                        )

                        st.session_state.questions[
                            next_index
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


        history = st.session_state.history


        # --------------------------------------------------
        # COLLECT SCORES
        # --------------------------------------------------


        overall_scores = [
            float(
                item["feedback"]["overall_score"]
            )
            for item in history
        ]


        technical_scores = [
            float(
                item["feedback"]["technical_accuracy"]
            )
            for item in history
        ]


        communication_scores = [
            float(
                item["feedback"]["communication"]
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
        # CALCULATE AVERAGES
        # --------------------------------------------------


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


        # --------------------------------------------------
        # OVERALL SCORE
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
        # SKILL ANALYTICS
        # --------------------------------------------------


        st.subheader(
            "🎯 Skill-wise Performance"
        )


        col1, col2 = st.columns(2)


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
        # TOPICS TO IMPROVE
        # --------------------------------------------------


        all_topics = []


        for item in history:

            all_topics.extend(
                item["feedback"][
                    "topics_to_improve"
                ]
            )


        topic_counts = {}


        for topic in all_topics:

            normalized_topic = (
                topic.strip().lower()
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

            for topic, count in sorted_topics[:5]:

                st.warning(
                    f"{topic.title()} — "
                    f"identified {count} time(s)"
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
                "Strengthen the identified "
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


            with st.expander(
                f"Question {index} — "
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
                    item["feedback"]["strengths"]
                ):

                    st.write(
                        f"✅ {strength}"
                    )


                st.markdown(
                    "**Areas to Improve**"
                )

                for weakness in (
                    item["feedback"]["weaknesses"]
                ):

                    st.write(
                        f"⚠️ {weakness}"
                    )


                st.markdown(
                    "**Improved Answer**"
                )

                st.info(
                    item["feedback"][
                        "improved_answer"
                    ]
                )


        # --------------------------------------------------
        # RESET INTERVIEW
        # --------------------------------------------------


        st.divider()


        if st.button(
            "🔄 Start New Interview",
            type="primary"
        ):

            reset_interview()

            st.rerun()
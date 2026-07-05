import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="AI Interview Copilot",
    page_icon="🤖",
    layout="wide"
)


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


initialize_session_state()


st.title(
    "🤖 AI Interview Copilot"
)

st.caption(
    "Adaptive AI-powered mock interviews "
    "personalized using your resume."
)


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

                st.write(
                    response.text
                )


else:

    questions = st.session_state.questions

    current_index = (
        st.session_state.current_question
    )

    total_questions = len(
        questions
    )


    if current_index < total_questions:

        current_question = (
            questions[current_index]
        )

        progress = (
            current_index / total_questions
        )

        st.progress(
            progress
        )

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

                            st.write(
                                error
                            )

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

                        st.write(
                            response.text
                        )


        if st.session_state.feedback is not None:

            feedback = (
                st.session_state.feedback
            )

            st.divider()

            st.header(
                "📊 Interview Feedback"
            )


            score = float(
                feedback["score"]
            )

            st.metric(
                "⭐ Score",
                f"{score:.1f}/10"
            )


            if score >= 8:

                st.success(
                    "🔥 Strong answer! "
                    "The next question "
                    "will be more challenging."
                )

            elif score <= 5:

                st.warning(
                    "📚 The next question "
                    "will focus on strengthening "
                    "your fundamentals."
                )

            else:

                st.info(
                    "👍 Good attempt. "
                    "The interviewer will explore "
                    "this topic further."
                )


            st.subheader(
                "✅ Strengths"
            )

            for strength in feedback["strengths"]:

                st.success(
                    strength
                )


            st.subheader(
                "⚠️ Areas to Improve"
            )

            for weakness in feedback["weaknesses"]:

                st.warning(
                    weakness
                )


            st.subheader(
                "💡 Improved Answer"
            )

            st.info(
                feedback["improved_answer"]
            )


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
                                        ]["score"]
                                    ),
                                    "weaknesses": (
                                        last_interview[
                                            "feedback"
                                        ]["weaknesses"]
                                    )
                                },
                                timeout=120
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


    else:

        st.success(
            "🎉 Interview Completed!"
        )

        st.header(
            "📊 Interview Summary"
        )


        scores = [
            float(
                item["feedback"]["score"]
            )
            for item in st.session_state.history
        ]


        if scores:

            average_score = (
                sum(scores)
                / len(scores)
            )

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Overall Interview Score",
                    f"{average_score:.1f}/10"
                )

            with col2:

                st.metric(
                    "Questions Answered",
                    len(
                        st.session_state.history
                    )
                )


            st.progress(
                min(
                    average_score / 10,
                    1.0
                )
            )


            if average_score >= 8:

                st.success(
                    "🔥 Strong Interview Performance"
                )

            elif average_score >= 6:

                st.info(
                    "👍 Good Interview Performance"
                )

            else:

                st.warning(
                    "📚 More Preparation Recommended"
                )


        st.divider()

        st.subheader(
            "📝 Interview History"
        )


        for index, item in enumerate(
            st.session_state.history,
            start=1
        ):

            score = float(
                item["feedback"]["score"]
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
                    "**Improved Answer**"
                )

                st.info(
                    item["feedback"][
                        "improved_answer"
                    ]
                )


        st.divider()


        if st.button(
            "🔄 Start New Interview",
            type="primary"
        ):

            reset_interview()

            st.rerun()
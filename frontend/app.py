import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="AI Interview Copilot",
    page_icon="🤖",
    layout="wide"
)


# ---------------- SESSION STATE ----------------

if "questions" not in st.session_state:
    st.session_state.questions = []

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "history" not in st.session_state:
    st.session_state.history = []

if "feedback" not in st.session_state:
    st.session_state.feedback = None

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False


# ---------------- HEADER ----------------

st.title("🤖 AI Interview Copilot")

st.caption(
    "Personalized AI-powered mock interviews based on your resume."
)


# ---------------- RESUME UPLOAD ----------------

if not st.session_state.interview_started:

    uploaded_file = st.file_uploader(
        "Upload your Resume",
        type=["pdf", "docx"]
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
                "Analyzing resume and preparing your interview..."
            ):

                response = requests.post(
                    f"{API_URL}/upload_resume",
                    files=files
                )

            if response.status_code == 200:

                data = response.json()

                st.session_state.questions = data["questions"]

                st.session_state.current_question = 0

                st.session_state.history = []

                st.session_state.feedback = None

                st.session_state.interview_started = True

                st.rerun()

            else:

                st.error(
                    "Failed to generate interview questions."
                )

                st.write(response.text)


# ---------------- INTERVIEW ----------------

else:

    questions = st.session_state.questions

    current_index = st.session_state.current_question

    total_questions = len(questions)

    if current_index < total_questions:

        current_question = questions[current_index]

        progress = current_index / total_questions

        st.progress(progress)

        st.caption(
            f"Question {current_index + 1} of {total_questions}"
        )

        st.subheader(
            f"🎤 {current_question}"
        )

        answer = st.text_area(
            "Your Answer",
            height=180,
            key=f"answer_{current_index}",
            placeholder="Type your interview answer here..."
        )

        if st.button(
            "Submit Answer",
            type="primary"
        ):

            if not answer.strip():

                st.warning(
                    "Please write an answer before submitting."
                )

            else:

                with st.spinner(
                    "AI interviewer is evaluating your answer..."
                ):

                    response = requests.post(
                        f"{API_URL}/evaluate",
                        json={
                            "question": current_question,
                            "answer": answer
                        }
                    )

                if response.status_code == 200:

                    feedback = response.json()

                    st.session_state.feedback = feedback

                    st.session_state.history.append(
                        {
                            "question": current_question,
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


        # ---------------- FEEDBACK ----------------

        if st.session_state.feedback is not None:

            feedback = st.session_state.feedback

            st.divider()

            st.header("📊 Interview Feedback")

            st.metric(
                "⭐ Score",
                f"{feedback['score']}/10"
            )

            st.subheader("✅ Strengths")

            for strength in feedback["strengths"]:
                st.success(strength)

            st.subheader("⚠️ Areas to Improve")

            for weakness in feedback["weaknesses"]:
                st.warning(weakness)

            st.subheader("💡 Improved Answer")

            st.info(
                feedback["improved_answer"]
            )

            if st.button(
                "Next Question ➡️"
            ):

                st.session_state.current_question += 1

                st.session_state.feedback = None

                st.rerun()


    # ---------------- INTERVIEW COMPLETE ----------------

    else:

        st.success(
            "🎉 Interview Completed!"
        )

        st.header(
            "📊 Interview Summary"
        )

        scores = [
            item["feedback"]["score"]
            for item in st.session_state.history
        ]

        if scores:

            average_score = sum(scores) / len(scores)

            st.metric(
                "Overall Interview Score",
                f"{average_score:.1f}/10"
            )

        st.write(
            f"Questions Answered: {len(st.session_state.history)}"
        )

        if st.button(
            "🔄 Start New Interview"
        ):

            st.session_state.clear()

            st.rerun()
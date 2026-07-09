import pandas as pd
import requests
import streamlit as st


API_URL = "https://ai-interview-copilot-7ewz.onrender.com"


# ==================================================
# PAGE CONFIG
# ==================================================


st.set_page_config(
    page_title="AI Interview Copilot",
    page_icon="🤖",
    layout="wide",
)


# ==================================================
# SESSION STATE
# ==================================================


def initialize_session_state():

    default_values = {
        "questions": [],
        "current_question": 0,
        "history": [],
        "feedback": None,
        "interview_started": False,
        "interview_id": None,
        "interview_completed": False,
        "prep_roadmap": None,
        "roadmap_answers_analyzed": 0,
        "voice_transcript": "",
        "target_role": "AI Engineer",
        "followup_active": False,
        "followup_question": "",
        "followup_topic": "",
        "followup_parent_index": None,
        "followup_used_for": [],
    }

    for key, value in default_values.items():

        if key not in st.session_state:

            st.session_state[key] = value


def reset_interview():

    keys_to_delete = [
        key
        for key in st.session_state.keys()
        if (
            key.startswith("answer_")
            or key.startswith("voice_answer_")
            or key.startswith("answer_mode_")
            or key.startswith("audio_")
            or key.startswith("followup_")
        )
    ]

    for key in keys_to_delete:

        del st.session_state[key]

    st.session_state.questions = []

    st.session_state.current_question = 0

    st.session_state.history = []

    st.session_state.feedback = None

    st.session_state.interview_started = False

    st.session_state.interview_id = None

    st.session_state.interview_completed = False

    st.session_state.voice_transcript = ""

    st.session_state.followup_active = False

    st.session_state.followup_question = ""

    st.session_state.followup_topic = ""

    st.session_state.followup_parent_index = None

    st.session_state.followup_used_for = []


def calculate_average(scores):

    if not scores:

        return 0.0

    return sum(scores) / len(scores)


def get_api_error(
    response,
    fallback_message: str,
) -> str:

    try:

        data = response.json()

        detail = data.get("detail")

        if isinstance(detail, str) and detail.strip():

            return detail.strip()

    except (ValueError, AttributeError):

        pass

    return fallback_message


def check_backend() -> bool:

    try:

        response = requests.get(
            f"{API_URL}/health",
            timeout=5,
        )

        return response.status_code == 200

    except requests.RequestException:

        return False


initialize_session_state()


# ==================================================
# SIDEBAR
# ==================================================


with st.sidebar:

    st.title("🤖 Interview Copilot")

    st.caption(
        "AI-powered adaptive "
        "interview platform"
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🎤 Mock Interview",
            "📚 Past Interviews",
            "🧠 AI Prep Roadmap",
        ],
    )

    st.divider()

    backend_online = check_backend()

    if backend_online:

        st.success(
            "Backend connected",
            icon="✅",
        )

    else:

        st.error(
            "Backend unavailable",
            icon="🚨",
        )

        st.caption(
            "Start FastAPI on port 8001 "
            "before using interview features."
        )

    st.divider()

    if st.session_state.interview_id is not None:

        st.caption(
            f"Current Interview ID: "
            f"{st.session_state.interview_id}"
        )


# ==================================================
# MOCK INTERVIEW
# ==================================================


if page == "🎤 Mock Interview":

    st.title("🤖 AI Interview Copilot")

    st.caption(
        "Adaptive AI-powered mock interviews "
        "personalized using your resume."
    )


    # ==============================================
    # START INTERVIEW
    # ==============================================


    if not st.session_state.interview_started:

        st.subheader("📄 Start Your Interview")

        target_role = st.selectbox(
            "🎯 Target Role",
            [
                "AI Engineer",
                "ML Engineer",
                "Data Scientist",
                "Data Analyst",
                "Backend Engineer",
            ],
            index=0,
            help=(
                "Questions, adaptive difficulty, and "
                "technical topics will be tailored "
                "to this role."
            ),
        )

        st.session_state.target_role = target_role

        uploaded_file = st.file_uploader(
            "Upload your Resume",
            type=[
                "pdf",
                "docx",
            ],
        )

        if uploaded_file is not None:

            if st.button(
                "🚀 Start Interview",
                type="primary",
            ):

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file,
                        uploaded_file.type,
                    )
                }

                with st.spinner(
                    "Analyzing your resume and "
                    "preparing interview questions..."
                ):

                    try:

                        response = requests.post(
                            f"{API_URL}/upload_resume",
                            files=files,
                            data={
                                "target_role": target_role,
                            },
                            timeout=120,
                        )

                    except requests.RequestException as error:

                        st.error(
                            "Unable to connect to backend."
                        )

                        st.write(error)

                        st.stop()

                if response.status_code == 200:

                    data = response.json()

                    interview_id = data.get(
                        "interview_id"
                    )

                    questions = data.get(
                        "questions",
                        [],
                    )

                    if interview_id is None:

                        st.error(
                            "Backend did not return "
                            "an interview ID."
                        )

                        st.stop()

                    if not questions:

                        st.error(
                            "No interview questions "
                            "were generated."
                        )

                        st.stop()

                    st.session_state.interview_id = (
                        interview_id
                    )

                    st.session_state.questions = questions

                    st.session_state.current_question = 0

                    st.session_state.history = []

                    st.session_state.feedback = None

                    st.session_state.voice_transcript = ""

                    st.session_state.followup_active = False

                    st.session_state.followup_question = ""

                    st.session_state.followup_topic = ""

                    st.session_state.followup_parent_index = None

                    st.session_state.followup_used_for = []

                    st.session_state.interview_completed = (
                        False
                    )

                    st.session_state.interview_started = True

                    st.rerun()

                else:

                    st.error(
                        get_api_error(
                            response,
                            "Failed to prepare the interview.",
                        )
                    )


    # ==============================================
    # ACTIVE INTERVIEW
    # ==============================================


    else:

        questions = st.session_state.questions

        current_index = (
            st.session_state.current_question
        )

        total_questions = len(questions)


        if current_index < total_questions:

            current_question_data = (
                questions[current_index]
            )

            if not isinstance(
                current_question_data,
                dict,
            ):

                st.error(
                    "Invalid question format."
                )

                st.stop()

            is_followup = (
                st.session_state.followup_active
            )

            if is_followup:

                current_question = (
                    st.session_state.followup_question
                )

                current_topic = (
                    st.session_state.followup_topic
                )

            else:

                current_question = (
                    current_question_data.get(
                        "question",
                        "",
                    )
                )

                current_topic = (
                    current_question_data.get(
                        "topic",
                        "general",
                    )
                )

            if not isinstance(
                current_question,
                str,
            ):

                st.error(
                    "Question must be a string."
                )

                st.stop()

            if not current_question.strip():

                st.error(
                    "Question is empty."
                )

                st.stop()


            # ======================================
            # PROGRESS
            # ======================================


            progress = (
                current_index
                / total_questions
            )

            st.progress(progress)

            col1, col2 = st.columns(2)

            with col1:

                st.caption(
                    (
                        "Follow-up for "
                        f"Question {current_index + 1}"
                        if is_followup
                        else (
                            f"Question {current_index + 1} "
                            f"of {total_questions}"
                        )
                    )
                )

            with col2:

                st.caption(
                    f"🎯 {st.session_state.target_role} | "
                    f"Topic: {current_topic.title()}"
                )

            if is_followup:

                st.info(
                    "🔎 The interviewer wants to probe "
                    "one point from your previous answer."
                )

                st.subheader(
                    f"🔎 Follow-up: {current_question}"
                )

            else:

                st.subheader(
                    f"🎤 {current_question}"
                )


            # ======================================
            # ANSWER MODE
            # ======================================


            st.subheader(
                "💬 Your Response"
            )

            question_key = (
                f"followup_{current_index}"
                if is_followup
                else f"main_{current_index}"
            )

            answer_mode = st.radio(
                "Choose answer mode",
                [
                    "⌨️ Type Answer",
                    "🎙️ Voice Answer",
                ],
                horizontal=True,
                key=(
                    f"answer_mode_{question_key}"
                ),
                disabled=(
                    st.session_state.feedback
                    is not None
                ),
            )


            # ======================================
            # VOICE ANSWER
            # ======================================


            if answer_mode == "🎙️ Voice Answer":

                st.caption(
                    "Record your interview answer. "
                    "Your speech will be converted "
                    "to text before evaluation."
                )

                voice_key = (
                    f"voice_answer_{question_key}"
                )

                if voice_key not in st.session_state:

                    st.session_state[voice_key] = ""

                audio_value = st.audio_input(
                    "🎙️ Record your answer",
                    key=(
                        f"audio_{question_key}"
                    ),
                    disabled=(
                        st.session_state.feedback
                        is not None
                    ),
                )

                if (
                    audio_value is not None
                    and st.session_state.feedback
                    is None
                ):

                    if st.button(
                        "✨ Transcribe Answer",
                        key=(
                            f"transcribe_{question_key}"
                        ),
                    ):

                        audio_bytes = (
                            audio_value.getvalue()
                        )

                        files = {
                            "file": (
                                "interview_answer.wav",
                                audio_bytes,
                                "audio/wav",
                            )
                        }

                        with st.spinner(
                            "Transcribing your answer..."
                        ):

                            try:

                                transcription_response = (
                                    requests.post(
                                        f"{API_URL}/transcribe",
                                        files=files,
                                        timeout=120,
                                    )
                                )

                            except requests.RequestException as error:

                                st.error(
                                    "Unable to transcribe audio."
                                )

                                st.write(error)

                                st.stop()

                        if (
                            transcription_response.status_code
                            == 200
                        ):

                            transcription_data = (
                                transcription_response.json()
                            )

                            transcript = (
                                transcription_data.get(
                                    "transcript",
                                    "",
                                )
                            )

                            if not transcript.strip():

                                st.error(
                                    "The transcription "
                                    "returned empty text."
                                )

                                st.stop()

                            # ==============================
                            # IMPORTANT VOICE STATE FIX
                            # ==============================

                            st.session_state.voice_transcript = (
                                transcript
                            )

                            st.session_state[
                                voice_key
                            ] = transcript

                            st.rerun()

                        else:

                            st.error(
                                get_api_error(
                                    transcription_response,
                                    "Audio transcription failed.",
                                )
                            )


                answer = st.text_area(
                    "Review your transcript",
                    height=180,
                    key=voice_key,
                    placeholder=(
                        "Your speech transcript "
                        "will appear here..."
                    ),
                    disabled=(
                        st.session_state.feedback
                        is not None
                    ),
                )

                st.session_state.voice_transcript = (
                    answer
                )

                if answer.strip():

                    st.success(
                        "🎙️ Audio transcribed "
                        "successfully. You can edit "
                        "the transcript before submitting."
                    )


            # ======================================
            # TYPE ANSWER
            # ======================================


            else:

                answer = st.text_area(
                    "Your Answer",
                    height=180,
                    key=(
                        f"answer_{question_key}"
                    ),
                    placeholder=(
                        "Type your interview "
                        "answer here..."
                    ),
                    disabled=(
                        st.session_state.feedback
                        is not None
                    ),
                )


            # ======================================
            # SUBMIT ANSWER
            # ======================================


            if st.session_state.feedback is None:

                if st.button(
                    "Submit Answer",
                    type="primary",
                ):

                    submitted_answer = answer.strip()

                    if not submitted_answer:

                        st.warning(
                            "Please provide an answer."
                        )

                    else:

                        evaluate_payload = {
                            "interview_id": (
                                st.session_state.interview_id
                            ),
                            "question_number": (
                                len(st.session_state.history) + 1
                            ),
                            "topic": current_topic,
                            "question": current_question,
                            "answer": submitted_answer,
                        }

                        with st.spinner(
                            "AI interviewer is "
                            "evaluating your answer..."
                        ):

                            try:

                                response = requests.post(
                                    f"{API_URL}/evaluate",
                                    json=evaluate_payload,
                                    timeout=120,
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
                                    "topic": current_topic,
                                    "question": current_question,
                                    "answer": submitted_answer,
                                    "feedback": feedback,
                                    "is_followup": is_followup,
                                    "main_question_index": current_index,
                                }
                            )

                            st.rerun()

                        else:

                            st.error(
                                get_api_error(
                                    response,
                                    "Answer evaluation failed.",
                                )
                            )


            # ======================================
            # FEEDBACK
            # ======================================


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

                st.metric(
                    "⭐ Overall Score",
                    f"{score:.1f}/10",
                )

                col1, col2, col3, col4 = (
                    st.columns(4)
                )

                with col1:

                    st.metric(
                        "🎯 Technical Accuracy",
                        (
                            f"{float(feedback['technical_accuracy']):.1f}"
                            "/10"
                        ),
                    )

                with col2:

                    st.metric(
                        "💬 Communication",
                        (
                            f"{float(feedback['communication']):.1f}"
                            "/10"
                        ),
                    )

                with col3:

                    st.metric(
                        "🧠 Depth",
                        (
                            f"{float(feedback['depth']):.1f}"
                            "/10"
                        ),
                    )

                with col4:

                    st.metric(
                        "📌 Relevance",
                        (
                            f"{float(feedback['relevance']):.1f}"
                            "/10"
                        ),
                    )

                if score >= 8:

                    st.success(
                        "🔥 Strong answer! "
                        "The next question will "
                        "be more challenging."
                    )

                elif score <= 5:

                    st.warning(
                        "📚 The next question will "
                        "focus on fundamentals."
                    )

                else:

                    st.info(
                        "👍 Good attempt. "
                        "The next question will use "
                        "medium difficulty."
                    )

                st.subheader(
                    "✅ Strengths"
                )

                for strength in feedback.get(
                    "strengths",
                    [],
                ):

                    st.success(strength)

                st.subheader(
                    "⚠️ Areas to Improve"
                )

                for weakness in feedback.get(
                    "weaknesses",
                    [],
                ):

                    st.warning(weakness)

                st.subheader(
                    "📚 Topics to Improve"
                )

                topics = feedback.get(
                    "topics_to_improve",
                    [],
                )

                if topics:

                    for topic in topics:

                        st.write(
                            f"• {topic}"
                        )

                else:

                    st.write(
                        "No specific topics identified."
                    )

                st.subheader(
                    "💡 Improved Answer"
                )

                st.info(
                    feedback.get(
                        "improved_answer",
                        (
                            "No improved "
                            "answer generated."
                        ),
                    )
                )


                # ==================================
                # FOLLOW-UP OR NEXT QUESTION
                # ==================================


                button_label = (
                    "Continue Interview ➡️"
                    if is_followup
                    else "Next Question ➡️"
                )

                if st.button(
                    button_label,
                    type="primary",
                ):

                    last_interview = (
                        st.session_state.history[-1]
                    )

                    # A follow-up has already been answered.
                    # Move to the next main topic.
                    if is_followup:

                        st.session_state.followup_active = False

                        st.session_state.followup_question = ""

                        st.session_state.followup_topic = ""

                        st.session_state.followup_parent_index = None

                        next_index = current_index + 1

                    else:

                        next_index = current_index + 1

                        followup_already_used = (
                            current_index
                            in st.session_state.followup_used_for
                        )

                        if not followup_already_used:

                            followup_payload = {
                                "question": last_interview["question"],
                                "answer": last_interview["answer"],
                                "score": last_interview[
                                    "feedback"
                                ]["overall_score"],
                                "weaknesses": last_interview[
                                    "feedback"
                                ].get(
                                    "weaknesses",
                                    [],
                                ),
                                "topic": current_topic,
                            }

                            with st.spinner(
                                "AI interviewer is deciding "
                                "whether to probe deeper..."
                            ):

                                try:

                                    followup_response = requests.post(
                                        (
                                            f"{API_URL}"
                                            "/followup_decision"
                                        ),
                                        json=followup_payload,
                                        timeout=120,
                                    )

                                except requests.RequestException as error:

                                    st.error(
                                        "Unable to generate "
                                        "follow-up decision."
                                    )

                                    st.write(error)

                                    st.stop()

                            if followup_response.status_code == 200:

                                followup_data = (
                                    followup_response.json()
                                )

                                ask_followup = followup_data.get(
                                    "ask_followup",
                                    False,
                                )

                                followup_question = followup_data.get(
                                    "followup_question",
                                    "",
                                )

                                if (
                                    ask_followup
                                    and followup_question.strip()
                                ):

                                    st.session_state.followup_active = True

                                    st.session_state.followup_question = (
                                        followup_question.strip()
                                    )

                                    st.session_state.followup_topic = (
                                        current_topic
                                    )

                                    st.session_state.followup_parent_index = (
                                        current_index
                                    )

                                    st.session_state.followup_used_for.append(
                                        current_index
                                    )

                                    st.session_state.feedback = None

                                    st.session_state.voice_transcript = ""

                                    st.rerun()

                            else:

                                st.error(
                                    get_api_error(
                                        followup_response,
                                        "Follow-up decision failed.",
                                    )
                                )

                                st.stop()


                    # Adapt the next MAIN question.
                    if next_index < total_questions:

                        next_question_data = (
                            st.session_state.questions[
                                next_index
                            ]
                        )

                        next_topic = (
                            next_question_data.get(
                                "topic",
                                "general",
                            )
                        )

                        adaptive_payload = {
                            "previous_question": (
                                last_interview["question"]
                            ),
                            "previous_answer": (
                                last_interview["answer"]
                            ),
                            "score": (
                                last_interview["feedback"][
                                    "overall_score"
                                ]
                            ),
                            "weaknesses": (
                                last_interview["feedback"].get(
                                    "weaknesses",
                                    [],
                                )
                            ),
                            "next_topic": next_topic,
                            "target_role": (
                                st.session_state.target_role
                            ),
                        }

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
                                    json=adaptive_payload,
                                    timeout=120,
                                )

                            except requests.RequestException as error:

                                st.error(
                                    "Unable to generate "
                                    "adaptive question."
                                )

                                st.write(error)

                                st.stop()

                        if adaptive_response.status_code == 200:

                            adaptive_question = (
                                adaptive_response.json().get(
                                    "question",
                                    "",
                                )
                            )

                            if not adaptive_question.strip():

                                st.error(
                                    "Adaptive question is empty."
                                )

                                st.stop()

                            st.session_state.questions[
                                next_index
                            ]["question"] = adaptive_question

                        else:

                            st.error(
                                get_api_error(
                                    adaptive_response,
                                    (
                                        "Adaptive question "
                                        "generation failed."
                                    ),
                                )
                            )

                            st.stop()


                    # Clear current answer widgets.
                    for key in list(st.session_state.keys()):

                        if (
                            key.startswith(
                                f"voice_answer_{question_key}"
                            )
                            or key.startswith(
                                f"answer_{question_key}"
                            )
                            or key.startswith(
                                f"audio_{question_key}"
                            )
                        ):

                            del st.session_state[key]

                    st.session_state.current_question = next_index

                    st.session_state.feedback = None

                    st.session_state.voice_transcript = ""

                    st.rerun()


        # ==========================================
        # INTERVIEW COMPLETED
        # ==========================================


        else:

            st.success(
                "🎉 Interview Completed!"
            )

            st.caption(
                f"Target role: "
                f"{st.session_state.target_role}"
            )

            if (
                not st.session_state.interview_completed
            ):

                try:

                    complete_response = requests.post(
                        (
                            f"{API_URL}"
                            "/complete_interview"
                        ),
                        json={
                            "interview_id": (
                                st.session_state.interview_id
                            )
                        },
                        timeout=30,
                    )

                    if (
                        complete_response.status_code
                        == 200
                    ):

                        st.session_state.interview_completed = (
                            True
                        )

                    else:

                        st.error(
                            get_api_error(
                                complete_response,
                                "Unable to complete interview.",
                            )
                        )

                except requests.RequestException as error:

                    st.error(
                        "Unable to complete interview."
                    )

                    st.write(error)


            history = st.session_state.history

            if history:

                overall_scores = [
                    float(
                        item["feedback"][
                            "overall_score"
                        ]
                    )
                    for item in history
                ]

                average_score = calculate_average(
                    overall_scores
                )

                st.header(
                    "📊 Interview Analytics"
                )

                st.metric(
                    "⭐ Final Interview Score",
                    f"{average_score:.1f}/10",
                )

                trend_data = pd.DataFrame(
                    {
                        "Question": [
                            f"Q{index}"
                            for index in range(
                                1,
                                len(overall_scores) + 1,
                            )
                        ],
                        "Score": overall_scores,
                    }
                ).set_index(
                    "Question"
                )

                st.subheader(
                    "📈 Performance Trend"
                )

                st.line_chart(
                    trend_data
                )


            try:

                report_response = requests.get(
                    (
                        f"{API_URL}/interviews/"
                        f"{st.session_state.interview_id}"
                        "/report"
                    ),
                    timeout=60,
                )

            except requests.RequestException:

                report_response = None


            if (
                report_response is not None
                and report_response.status_code == 200
            ):

                st.download_button(
                    label=(
                        "📥 Download Interview Report"
                    ),
                    data=report_response.content,
                    file_name=(
                        f"interview_report_"
                        f"{st.session_state.interview_id}"
                        ".pdf"
                    ),
                    mime="application/pdf",
                    type="primary",
                )


            st.divider()

            if st.button(
                "🔄 Start New Interview"
            ):

                reset_interview()

                st.rerun()


# ==================================================
# PAST INTERVIEWS
# ==================================================


elif page == "📚 Past Interviews":

    st.title(
        "📚 Past Interviews"
    )

    st.caption(
        "Review interview history and "
        "track your performance over time."
    )

    try:

        response = requests.get(
            f"{API_URL}/interviews",
            timeout=30,
        )

    except requests.RequestException as error:

        st.error(
            "Unable to connect to backend."
        )

        st.write(error)

        st.stop()

    if response.status_code != 200:

        st.error(
            get_api_error(
                response,
                "Unable to load interview history.",
            )
        )

        st.stop()

    interviews = response.json().get(
        "interviews",
        [],
    )

    if not interviews:

        st.info(
            "No interview history found."
        )

        st.stop()

    completed_interviews = [
        interview
        for interview in interviews
        if interview.get("completed") == 1
    ]

    completed_scores = [
        float(interview["overall_score"])
        for interview in completed_interviews
        if interview.get("overall_score") is not None
    ]

    average_score = calculate_average(
        completed_scores
    )

    best_score = (
        max(completed_scores)
        if completed_scores
        else 0.0
    )

    st.subheader(
        "📊 Interview Summary"
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:

        st.metric(
            "🎤 Total Interviews",
            len(interviews),
        )

    with col2:

        st.metric(
            "✅ Completed",
            len(completed_interviews),
        )

    with col3:

        st.metric(
            "⭐ Average Score",
            f"{average_score:.1f}/10",
        )

    with col4:

        st.metric(
            "🏆 Best Score",
            f"{best_score:.1f}/10",
        )

    if completed_scores:

        st.subheader(
            "📈 Performance Over Time"
        )

        performance_rows = []

        for interview in reversed(
            completed_interviews
        ):

            if (
                interview.get("overall_score")
                is not None
            ):

                performance_rows.append(
                    {
                        "Interview": (
                            f"Interview "
                            f"#{interview['id']}"
                        ),
                        "Score": float(
                            interview["overall_score"]
                        ),
                    }
                )

        performance_data = pd.DataFrame(
            performance_rows
        )

        if not performance_data.empty:

            st.line_chart(
                performance_data.set_index(
                    "Interview"
                )
            )

    st.divider()

    st.subheader(
        "🔍 Review Interview"
    )

    interview_options = {}

    for interview in interviews:

        score = interview.get(
            "overall_score"
        )

        if score is None:

            score_text = "In Progress"

        else:

            score_text = (
                f"{float(score):.1f}/10"
            )

        label = (
            f"Interview #{interview['id']} | "
            f"{interview['resume_filename']} | "
            f"{score_text}"
        )

        interview_options[label] = (
            interview["id"]
        )

    selected_label = st.selectbox(
        "Select Interview",
        list(
            interview_options.keys()
        ),
    )

    selected_interview_id = (
        interview_options[
            selected_label
        ]
    )

    try:

        detail_response = requests.get(
            (
                f"{API_URL}/interviews/"
                f"{selected_interview_id}"
            ),
            timeout=30,
        )

    except requests.RequestException as error:

        st.error(
            "Unable to load interview details."
        )

        st.write(error)

        st.stop()

    if detail_response.status_code != 200:

        st.error(
            get_api_error(
                detail_response,
                "Failed to load interview details.",
            )
        )

        st.stop()

    answers = detail_response.json().get(
        "answers",
        [],
    )

    if not answers:

        st.warning(
            "This interview has no "
            "saved answers yet."
        )

        st.stop()


    st.subheader(
        "📄 Interview Report"
    )

    try:

        report_response = requests.get(
            (
                f"{API_URL}/interviews/"
                f"{selected_interview_id}"
                "/report"
            ),
            timeout=60,
        )

    except requests.RequestException:

        report_response = None

    if (
        report_response is not None
        and report_response.status_code == 200
    ):

        st.download_button(
            label=(
                "📥 Download Interview Report"
            ),
            data=report_response.content,
            file_name=(
                f"interview_report_"
                f"{selected_interview_id}.pdf"
            ),
            mime="application/pdf",
            type="primary",
        )


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

    st.subheader(
        f"📊 Interview "
        f"#{selected_interview_id} Analytics"
    )

    st.metric(
        "⭐ Interview Score",
        f"{average_overall:.1f}/10",
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:

        st.metric(
            "🎯 Technical",
            f"{average_technical:.1f}/10",
        )

    with col2:

        st.metric(
            "💬 Communication",
            f"{average_communication:.1f}/10",
        )

    with col3:

        st.metric(
            "🧠 Depth",
            f"{average_depth:.1f}/10",
        )

    with col4:

        st.metric(
            "📌 Relevance",
            f"{average_relevance:.1f}/10",
        )

    st.subheader(
        "📈 Question Performance"
    )

    question_data = pd.DataFrame(
        {
            "Question": [
                f"Q{answer['question_number']}"
                for answer in answers
            ],
            "Score": overall_scores,
        }
    ).set_index(
        "Question"
    )

    st.line_chart(
        question_data
    )

    st.subheader(
        "🎯 Skill Comparison"
    )

    skill_data = pd.DataFrame(
        {
            "Skill": [
                "Technical Accuracy",
                "Communication",
                "Depth",
                "Relevance",
            ],
            "Score": [
                average_technical,
                average_communication,
                average_depth,
                average_relevance,
            ],
        }
    ).set_index(
        "Skill"
    )

    st.bar_chart(
        skill_data
    )

    st.divider()

    st.subheader(
        "📝 Questions and Feedback"
    )

    for answer_data in answers:

        answer_topic = (
            answer_data["topic"]
            .replace("_", " ")
            .title()
        )

        score = float(
            answer_data["overall_score"]
        )

        with st.expander(
            (
                f"Question "
                f"{answer_data['question_number']} | "
                f"{answer_topic} | "
                f"{score:.1f}/10"
            )
        ):

            st.markdown(
                "**Question**"
            )

            st.write(
                answer_data["question"]
            )

            st.markdown(
                "**Your Answer**"
            )

            st.write(
                answer_data["answer"]
            )

            st.markdown(
                "**Strengths**"
            )

            for strength in answer_data.get(
                "strengths",
                [],
            ):

                st.write(
                    f"✅ {strength}"
                )

            st.markdown(
                "**Areas to Improve**"
            )

            for weakness in answer_data.get(
                "weaknesses",
                [],
            ):

                st.write(
                    f"⚠️ {weakness}"
                )

            st.markdown(
                "**Topics to Improve**"
            )

            for topic_to_improve in answer_data.get(
                "topics_to_improve",
                [],
            ):

                st.write(
                    f"📚 {topic_to_improve}"
                )

            st.markdown(
                "**Improved Answer**"
            )

            st.info(
                answer_data.get(
                    "improved_answer",
                    (
                        "No improved "
                        "answer recorded."
                    ),
                )
            )


# ==================================================
# AI PREP ROADMAP
# ==================================================


elif page == "🧠 AI Prep Roadmap":

    st.title(
        "🧠 AI Prep Roadmap"
    )

    st.caption(
        "Generate a personalized 7-day "
        "interview preparation plan based "
        "on your previous interview performance."
    )

    st.info(
        "The AI analyzes your saved interview "
        "scores, weaknesses, and improvement "
        "topics to build your preparation plan."
    )

    col1, col2 = st.columns(
        [
            1,
            3,
        ]
    )

    with col1:

        generate_button = st.button(
            "✨ Generate My Roadmap",
            type="primary",
            use_container_width=True,
        )

    with col2:

        if (
            st.session_state.prep_roadmap
            is not None
        ):

            if st.button(
                "🔄 Regenerate Roadmap"
            ):

                st.session_state.prep_roadmap = None

                st.session_state.roadmap_answers_analyzed = 0

                st.rerun()

    if generate_button:

        with st.spinner(
            "AI coach is analyzing your "
            "interview history and building "
            "your personalized roadmap..."
        ):

            try:

                roadmap_response = requests.post(
                    f"{API_URL}/prep_roadmap",
                    timeout=180,
                )

            except requests.RequestException as error:

                st.error(
                    "Unable to generate roadmap."
                )

                st.write(error)

                st.stop()

        if roadmap_response.status_code == 200:

            roadmap_data = (
                roadmap_response.json()
            )

            st.session_state.prep_roadmap = (
                roadmap_data.get(
                    "roadmap"
                )
            )

            st.session_state.roadmap_answers_analyzed = (
                roadmap_data.get(
                    "total_answers_analyzed",
                    0,
                )
            )

            st.rerun()

        else:

            st.error(
                get_api_error(
                    roadmap_response,
                    "Roadmap generation failed.",
                )
            )


    roadmap = (
        st.session_state.prep_roadmap
    )

    if roadmap is not None:

        st.divider()

        st.caption(
            f"Analyzed "
            f"{st.session_state.roadmap_answers_analyzed} "
            f"saved interview answer(s)"
        )

        st.header(
            "🎯 Interview Readiness"
        )

        st.metric(
            "Current Readiness Level",
            roadmap.get(
                "readiness_level",
                "Unknown",
            ),
        )

        st.info(
            roadmap.get(
                "readiness_summary",
                (
                    "No readiness summary "
                    "was generated."
                ),
            )
        )

        st.header(
            "🔥 Priority Areas"
        )

        priority_areas = roadmap.get(
            "priority_areas",
            [],
        )

        for priority_data in priority_areas:

            priority = priority_data.get(
                "priority"
            )

            topic = priority_data.get(
                "topic",
                "Unknown Topic",
            )

            with st.expander(
                (
                    f"Priority {priority}: "
                    f"{topic}"
                ),
                expanded=(
                    priority == 1
                ),
            ):

                st.markdown(
                    "**Why this is a priority**"
                )

                st.write(
                    priority_data.get(
                        "reason",
                        "",
                    )
                )

                st.markdown(
                    "**Focus Topics**"
                )

                for focus_topic in priority_data.get(
                    "focus_topics",
                    [],
                ):

                    st.write(
                        f"🎯 {focus_topic}"
                    )

        st.header(
            "📅 Your 7-Day Preparation Plan"
        )

        seven_day_plan = roadmap.get(
            "seven_day_plan",
            [],
        )

        for day_data in seven_day_plan:

            day = day_data.get(
                "day"
            )

            title = day_data.get(
                "title",
                "Preparation Day",
            )

            st.subheader(
                f"Day {day} — {title}"
            )

            st.caption(
                f"⏱️ Estimated Study Time: "
                f"{day_data.get('estimated_hours', 0)} "
                f"hour(s)"
            )

            st.markdown(
                "**Topics**"
            )

            for topic in day_data.get(
                "topics",
                [],
            ):

                st.write(
                    f"• {topic}"
                )

            st.markdown(
                "**Practice Task**"
            )

            st.success(
                day_data.get(
                    "practice_task",
                    "",
                )
            )

            if day != 7:

                st.divider()

        st.header(
            "💼 Interview Strategy"
        )

        for index, strategy in enumerate(
            roadmap.get(
                "interview_strategy",
                [],
            ),
            start=1,
        ):

            st.write(
                f"**{index}.** {strategy}"
            )

        st.header(
            "🚀 Final Recommendation"
        )

        st.success(
            roadmap.get(
                "final_recommendation",
                (
                    "Continue practicing "
                    "your interview skills."
                ),
            )
        )
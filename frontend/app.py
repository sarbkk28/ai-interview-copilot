import streamlit as st
import requests

st.set_page_config(
    page_title="AI Interview Copilot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Interview Copilot")

uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf", "docx"]
)

if uploaded_file is not None:

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file,
            uploaded_file.type
        )
    }

    with st.spinner("Generating Interview Questions..."):

        response = requests.post(
            "http://127.0.0.1:8000/upload_resume",
            files=files
        )

    if response.status_code == 200:

        data = response.json()

        st.success("Resume Uploaded Successfully!")

        st.subheader("📄 Extracted Resume")

        st.text_area(
            "Resume",
            data["resume_text"],
            height=250
        )

        st.subheader("📝 Interview Questions")

        st.markdown(data["questions"])

        st.divider()

        st.header("🎯 AI Interview Evaluation")

        question = st.text_input(
            "Paste an Interview Question"
        )

        answer = st.text_area(
            "Write Your Answer"
        )

        if st.button("Evaluate Answer"):

            if question.strip() == "" or answer.strip() == "":
                st.warning("Please enter both question and answer.")

            else:

                with st.spinner("Evaluating..."):

                    eval_response = requests.post(
                        "http://127.0.0.1:8000/evaluate",
                        json={
                            "question": question,
                            "answer": answer
                        }
                    )

                if eval_response.status_code == 200:

                    feedback = eval_response.json()

                    st.success("Evaluation Completed!")

                    st.metric(
                        "⭐ Score",
                        f"{feedback['score']}/10"
                    )

                    st.subheader("✅ Strengths")

                    for strength in feedback["strengths"]:
                        st.success(strength)

                    st.subheader("❌ Weaknesses")

                    for weakness in feedback["weaknesses"]:
                        st.error(weakness)

                    st.subheader("💡 Improved Answer")

                    st.info(feedback["improved_answer"])

                else:
                    st.error("Evaluation Failed")

    else:
        st.error("Failed to upload resume.")
import streamlit as st
import requests

st.set_page_config(
    page_title="AI Interview Copilot",
    page_icon="🤖"
)

st.title("🤖 AI Interview Copilot")

uploaded_file = st.file_uploader(
    "Upload your Resume",
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

    response = requests.post(
        "http://127.0.0.1:8000/upload_resume",
        files=files
    )

    if response.status_code == 200:

        data = response.json()

        st.success("Resume Uploaded Successfully!")

        st.subheader("Extracted Resume")
        st.text_area(
            "",
            data["resume_text"],
            height=500
        )

        st.subheader("Generated Interview Questions")
        st.markdown(data["questions"])

    else:
        st.error("Something went wrong.")
        st.write(response.text)
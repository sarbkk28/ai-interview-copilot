import pdfplumber
from docx import Document


def extract_text(file_path: str) -> str:
    """
    Extract text from a PDF or DOCX resume.
    """

    if file_path.endswith(".pdf"):
        text = ""

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        return text

    elif file_path.endswith(".docx"):
        doc = Document(file_path)

        text = "\n".join([para.text for para in doc.paragraphs])

        return text

    else:
        raise ValueError("Unsupported file format.")
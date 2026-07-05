import os

import pdfplumber
from docx import Document


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx"
}


def extract_pdf_text(
    file_path: str
) -> str:
    """
    Extract text from a PDF document.
    """

    text_parts = []

    with pdfplumber.open(file_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts)


def extract_docx_text(
    file_path: str
) -> str:
    """
    Extract text from a DOCX document.
    """

    document = Document(file_path)

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs)


def extract_text(
    file_path: str
) -> str:
    """
    Extract text from a supported resume file.
    """

    extension = os.path.splitext(
        file_path
    )[1].lower()

    if extension not in SUPPORTED_EXTENSIONS:

        raise ValueError(
            "Unsupported resume format. "
            "Only PDF and DOCX are supported."
        )

    if extension == ".pdf":

        text = extract_pdf_text(
            file_path
        )

    else:

        text = extract_docx_text(
            file_path
        )

    if not text.strip():

        raise ValueError(
            "Unable to extract text from resume."
        )

    return text
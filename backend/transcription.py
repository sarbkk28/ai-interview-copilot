import os
import tempfile

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


api_key = os.getenv("GROQ_API_KEY")


if not api_key:

    raise ValueError(
        "GROQ_API_KEY is missing from .env"
    )


client = Groq(
    api_key=api_key
)


def transcribe_audio(
    audio_bytes: bytes,
    filename: str = "answer.wav",
) -> str:

    if not audio_bytes:

        raise ValueError(
            "Audio data is empty."
        )


    file_extension = os.path.splitext(
        filename
    )[1]


    if not file_extension:

        file_extension = ".wav"


    temporary_file_path = None


    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension,
        ) as temporary_file:

            temporary_file.write(
                audio_bytes
            )


            temporary_file_path = (
                temporary_file.name
            )


        with open(
            temporary_file_path,
            "rb",
        ) as audio_file:

            transcription = (
                client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3-turbo",
                    response_format="json",
                    temperature=0.0,
                )
            )


        transcript = transcription.text


        if transcript is None:

            raise ValueError(
                "Groq returned no transcription."
            )


        if not transcript.strip():

            raise ValueError(
                "Groq returned an empty transcription."
            )


        return transcript.strip()


    except Exception as error:

        print(
            "TRANSCRIPTION ERROR:",
            repr(error),
        )


        raise ValueError(
            f"Audio transcription failed: {error}"
        ) from error


    finally:

        if (
            temporary_file_path
            and os.path.exists(
                temporary_file_path
            )
        ):

            os.remove(
                temporary_file_path
            )
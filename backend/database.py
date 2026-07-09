import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "interview.db"


def get_database_connection():
    """
    Create and return a SQLite database connection.
    """

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """
    Create database tables if they do not exist.
    """

    connection = get_database_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_filename TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed INTEGER DEFAULT 0,
            overall_score REAL
        )
        """
    )


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS interview_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            topic TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            overall_score REAL NOT NULL,
            technical_accuracy REAL NOT NULL,
            communication REAL NOT NULL,
            depth REAL NOT NULL,
            relevance REAL NOT NULL,
            strengths TEXT,
            weaknesses TEXT,
            topics_to_improve TEXT,
            improved_answer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (interview_id)
            REFERENCES interviews(id)
        )
        """
    )


    connection.commit()

    connection.close()


    print(
        "✅ SQLite database initialized"
    )
import os
from datetime import datetime

_conn = None   


def init_db() -> bool:
   
    global _conn

    required = ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME")
    if not all(os.environ.get(k) for k in required):
        print("DB: MySQL env vars not set – persistence disabled.")
        return False

    try:
        import mysql.connector
        _conn = mysql.connector.connect(
            host     = os.environ["DB_HOST"],
            port     = int(os.environ.get("DB_PORT", 3306)),
            user     = os.environ["DB_USER"],
            password = os.environ["DB_PASSWORD"],
            database = os.environ["DB_NAME"],
        )
        cursor = _conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS qa_log (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                session_id  VARCHAR(36)  NOT NULL,
                question    TEXT         NOT NULL,
                context     MEDIUMTEXT,
                answer      TEXT,
                created_at  DATETIME     NOT NULL
            )
        """)
        _conn.commit()
        cursor.close()
        print("DB: MySQL connected and qa_log table ready.")
        return True

    except Exception as exc:
        print(f"DB: Could not connect to MySQL ({exc}) – persistence disabled.")
        _conn = None
        return False


def log_qa(
    session_id: str,
    question: str,
    context: str,
    answer: str,
) -> None:
    """
    Insert one Q&A record into qa_log. Silently ignores errors.
    """
    if _conn is None:
        return
    try:
        cursor = _conn.cursor()
        cursor.execute(
            """INSERT INTO qa_log (session_id, question, context, answer, created_at)
               VALUES (%s, %s, %s, %s, %s)""",
            (session_id, question, context, answer, datetime.utcnow()),
        )
        _conn.commit()
        cursor.close()
    except Exception as exc:
        print(f"DB: Failed to log Q&A: {exc}")

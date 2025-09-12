import sqlite3
from datetime import timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9), "JST")
this_file_path = Path(__file__).resolve()

project_root_dir = this_file_path.parent.parent.parent

DB_PATH = project_root_dir / "client" / "audily.db"


def create_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"データベース接続エラー: {e}")
        return None


def setup_database():

    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS operation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                source_filename TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            );
            """
            )
            conn.commit()
            print("'operation_history' テーブルの準備が完了しました。")
        except sqlite3.Error as e:
            print(f"テーブル作成エラー: {e}")
        finally:
            conn.close()


def log_operation(user_id: str, operation_type: str, source_filename: str, status: str):

    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
            INSERT INTO operation_history (user_id, operation_type, source_filename, status)
            VALUES (?, ?, ?, ?);
            """,
                (user_id, operation_type, source_filename, status),
            )
            conn.commit()
            print(
                f"履歴を記録しました: User({user_id}), Op({operation_type}), File({source_filename})"
            )
        except sqlite3.Error as e:
            print(f"履歴の記録に失敗しました: {e}")
        finally:
            conn.close()


def get_history_by_user_id(user_id: str) -> list:

    conn = create_connection()
    conn.row_factory = sqlite3.Row
    history_records = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
            SELECT id, operation_type, source_filename, status, created_at
            FROM operation_history
            WHERE user_id = ?
            ORDER BY created_at DESC;
            """,
                (user_id,),
            )
            rows = cursor.fetchall()
            history_records = [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"履歴の取得に失敗しました: {e}")
        finally:
            conn.close()
    return history_records

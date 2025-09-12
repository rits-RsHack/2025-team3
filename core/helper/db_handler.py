import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9), "JST")

this_file_path = Path(__file__).resolve()
project_root_dir = this_file_path.parent.parent.parent
DB_PATH = project_root_dir / "client" / "audily.db"


def adapt_datetime_to_iso(dt: datetime):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=JST)
    return dt.isoformat().encode("utf8")


sqlite3.register_adapter(datetime, adapt_datetime_to_iso)


def create_connection():
    print(f"DEBUG: データベースに接続しようとしています: {DB_PATH}")
    if not DB_PATH.exists():
        print(
            f"ERROR: データベースファイルが見つかりません。パスを確認してください: {DB_PATH}"
        )
        if not DB_PATH.parent.exists():
            print(
                f"ERROR: データベースファイルの親ディレクトリが存在しません: {DB_PATH.parent}"
            )
        return None
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        print(f"ERROR: データベース接続エラー: {e}")
        return None


def setup_database():

    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # created_atカラムをTEXT型に変更し、DEFAULT値を削除
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS operation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                source_filename TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user (id)
            );
            """
            )
            conn.commit()
            print("INFO: 'operation_history' テーブルの準備が完了しました。")
        except sqlite3.Error as e:
            print(f"ERROR: テーブル作成エラー: {e}")
        finally:
            conn.close()


def log_operation(user_id: str, operation_type: str, source_filename: str, status: str):

    conn = create_connection()
    if conn:
        try:
            current_time_jst = datetime.now(JST)

            cursor = conn.cursor()
            cursor.execute(
                """
            INSERT INTO operation_history (user_id, operation_type, source_filename, status, created_at)
            VALUES (?, ?, ?, ?, ?);
            """,
                (user_id, operation_type, source_filename, status, current_time_jst),
            )
            conn.commit()
            print(
                f"INFO: 履歴を記録しました: User({user_id}), Op({operation_type}), File({source_filename}), Time({current_time_jst.isoformat()})"
            )
        except sqlite3.Error as e:
            print(f"ERROR: 履歴の記録に失敗しました: {e}")
        finally:
            conn.close()


def get_history_by_user_id(user_id: str) -> list:

    conn = create_connection()
    if not conn:
        return []

    conn.row_factory = sqlite3.Row
    history_records = []

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
        print(f"ERROR: 履歴の取得に失敗しました: {e}")
    finally:
        if conn:
            conn.close()

    return history_records

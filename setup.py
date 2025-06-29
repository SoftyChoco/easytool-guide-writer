# 0_setup_database.py (structured_data_json 컬럼 추가)
import os
import sqlite3

DB_NAME = "easytool_content.db"

def setup_database():
    """DB를 새로 생성합니다. (articles에 structured_data_json 추가)"""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 파이프라인 로그 테이블 (변경 없음)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, tool_name TEXT NOT NULL, status TEXT NOT NULL,
        creator_draft TEXT, editor_revision TEXT, decider_judgment_json TEXT, rejection_reason TEXT,
        created_at DATETIME, updated_at DATETIME
    )""")

    # 최종 발행 콘텐츠 테이블 (컬럼 추가)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pipeline_log_id INTEGER,
        tool_name TEXT NOT NULL,
        title TEXT NOT NULL,
        meta_description TEXT,
        content_markdown TEXT NOT NULL,
        structured_data_json TEXT, -- <<< FAQ 등 구조화된 데이터를 위한 컬럼
        published_at DATETIME,
        FOREIGN KEY (pipeline_log_id) REFERENCES pipeline_logs (id)
    )
    """)

    conn.commit()
    conn.close()
    print(f"데이터베이스 '{DB_NAME}'가 새로운 스키마로 성공적으로 준비되었습니다.")

if __name__ == "__main__":
    setup_database()

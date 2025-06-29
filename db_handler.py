# db_handler.py
import sqlite3
import datetime
import json

DB_NAME = "easytool_content.db"

# --- Datetime 어댑터/컨버터 ---
def adapt_datetime_iso(val):
    """datetime 객체를 ISO 8601 문자열로 변환합니다."""
    return val.isoformat()

def convert_datetime_iso(s):
    """ISO 8601 문자열을 datetime 객체로 변환합니다."""
    return datetime.datetime.fromisoformat(s.decode('utf-8'))

# sqlite3에 새로운 변환 규칙을 등록합니다.
sqlite3.register_adapter(datetime.datetime, adapt_datetime_iso)
sqlite3.register_converter("datetime", convert_datetime_iso)

def db_connect():
    """데이터베이스 커넥션을 생성합니다."""
    return sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES)

def get_published_tool_names(conn):
    """'articles' 테이블에서 이미 발행된 글의 tool_name 목록을 가져옵니다."""
    cursor = conn.cursor()
    cursor.execute("SELECT tool_name FROM articles")
    return [row[0] for row in cursor.fetchall()]

def create_pipeline_entry(conn, tool_name):
    """'pipeline_logs'에 새로운 작업 로그를 생성하고 ID를 반환합니다."""
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pipeline_logs (tool_name, status, created_at, updated_at) VALUES (?, ?, ?, ?)",
                   (tool_name, 'INITIATED', datetime.datetime.now(), datetime.datetime.now()))
    conn.commit()
    return cursor.lastrowid

def update_pipeline_step(conn, pipeline_id, **kwargs):
    """'pipeline_logs'의 현재 작업 로그를 업데이트합니다."""
    kwargs['updated_at'] = datetime.datetime.now()
    fields = ', '.join([f"{key} = ?" for key in kwargs.keys()])
    values = list(kwargs.values())
    values.append(pipeline_id)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE pipeline_logs SET {fields} WHERE id = ?", values)
    conn.commit()

def save_approved_article(conn, pipeline_id, tool_name, final_content, article_data):
    """승인된 아티클과 관련 메타데이터를 'articles' 테이블에 저장합니다."""
    print("\n" + "="*50)
    print("🤖 AI 최종결정자 승인! 콘텐츠를 자동으로 저장합니다.")
    print(f"   - 제목: {article_data['title']}")
    print("="*50)
    
    update_pipeline_step(conn, pipeline_id, status='AUTO_APPROVED')
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO articles (
            pipeline_log_id, tool_name, title, meta_description, 
            content_markdown, structured_data_json, published_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        pipeline_id, 
        tool_name, 
        article_data['title'], 
        article_data['meta_description'],
        final_content,
        json.dumps(article_data['faq_json_ld'], ensure_ascii=False),
        datetime.datetime.now()
    ))
    conn.commit()
    print("\n🎉 'articles' 테이블에 콘텐츠가 성공적으로 저장되었습니다.")

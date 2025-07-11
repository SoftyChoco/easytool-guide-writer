#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트입니다.
필요한 테이블을 생성하고 기본 스키마를 설정합니다.
"""
import sqlite3
import os

DB_NAME = "easytool_content.db"

def init_database():
    """데이터베이스와 필요한 테이블들을 초기화합니다."""
    print("🔄 데이터베이스 초기화를 시작합니다...")
    
    # 기존 DB 파일 존재 여부 확인 및 백업
    if os.path.exists(DB_NAME):
        backup_file = f"{DB_NAME}.backup"
        try:
            os.rename(DB_NAME, backup_file)
            print(f"⚠️ 기존 데이터베이스 파일을 {backup_file}으로 백업했습니다.")
        except Exception as e:
            print(f"❌ 데이터베이스 백업 중 오류 발생: {e}")
            return False
    
    # 데이터베이스 연결 및 테이블 생성
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # pipeline_logs 테이블 생성 (작업 로그)
        cursor.execute('''
        CREATE TABLE pipeline_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_name TEXT NOT NULL,
            status TEXT NOT NULL,
            locale TEXT NOT NULL DEFAULT 'ko',
            creator_draft TEXT,
            editor_revision TEXT,
            decider_judgment_json TEXT,
            rejection_reason TEXT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
        ''')
        
        # articles 테이블 생성 (승인된 콘텐츠)
        cursor.execute('''
        CREATE TABLE articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pipeline_log_id INTEGER,
            tool_name TEXT NOT NULL,
            title TEXT NOT NULL,
            meta_description TEXT,
            content_markdown TEXT NOT NULL,
            structured_data_json TEXT,
            published_at DATETIME,
            locale TEXT NOT NULL DEFAULT 'ko',
            FOREIGN KEY (pipeline_log_id) REFERENCES pipeline_logs (id)
        )
        ''')
        
        conn.commit()
        print("✅ 데이터베이스 및 테이블이 생성되었습니다!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ 데이터베이스 초기화 중 오류 발생: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if init_database():
        print("\n🎉 성공적으로 데이터베이스를 초기화했습니다.")
        print("📝 이제 main.py를 실행하여 콘텐츠 생성 파이프라인을 시작할 수 있습니다.")
    else:
        print("\n⚠️ 데이터베이스 초기화에 실패했습니다.") 
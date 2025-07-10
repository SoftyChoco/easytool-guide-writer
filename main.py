# main.py (config.py 의존성 제거 및 최종 수정 완료)
import json
import logging
from db_handler import (
    db_connect, get_published_tool_names, create_pipeline_entry,
    update_pipeline_step, save_approved_article
)
from agents import (
    setup_gemini, run_ai_agent, PipelineError, logger
)
from feature import FEATURES_JSON

# 로거 가져오기 - agents.py에서 이미 설정됨
logger = logging.getLogger('easytool')

def load_prompt(file_path):
    """지정된 경로의 텍스트 파일(프롬프트)을 읽어옵니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        error_msg = f"프롬프트 파일을 찾을 수 없습니다: {file_path}"
        logger.error(error_msg)
        raise PipelineError(error_msg)

def select_new_topic(all_features, published_tools):
    """발행되지 않은 새로운 주제(기능)를 선택합니다."""
    available_tools = [f for f in all_features if isinstance(f, dict) and f.get('name') not in published_tools]
    return available_tools[0] if available_tools else None

def run_pipeline(conn, model):
    """
    콘텐츠 생성의 전체 파이프라인을 순차적으로 실행하고 관리합니다.
    """
    try:
        # 1. 프롬프트 로딩 및 주제 선정
        CREATOR_PROMPT = load_prompt('prompts/creator.md')
        EDITOR_PROMPT = load_prompt('prompts/editor.md')
        DECIDER_PROMPT = load_prompt('prompts/decider.md')
        
        published_tools = get_published_tool_names(conn)
        selected_tool = select_new_topic(FEATURES_JSON, published_tools)
        
        if not selected_tool:
            print("🎉 모든 주제에 대한 글 작성이 완료되었습니다!")
            return 'COMPLETE'

        print(f"🚀 이번에 작성할 콘텐츠 주제는 '{selected_tool['name']}' 입니다.")
        
        # 2. 파이프라인 시작 및 ID 생성
        pipeline_id = create_pipeline_entry(conn, selected_tool['name'])
        print(f"파이프라인 시작 (ID: {pipeline_id})")
        logger.info(f"파이프라인 시작 (ID: {pipeline_id}, 주제: {selected_tool['name']})")

        # 3. Agent 파이프라인 순차 실행
        # Step 1: 작성자
        creator_result = run_ai_agent(model, "작성자", CREATOR_PROMPT.format(**selected_tool), is_json_output=True)
        creator_draft = creator_result['article_markdown']
        article_meta_data = {
            "title": creator_result.get('title', selected_tool['name']),
            "meta_description": creator_result.get('meta_description', ''),
            "faq_json_ld": creator_result.get('faq_json_ld', {})
        }
        update_pipeline_step(conn, pipeline_id, creator_draft=creator_draft, status='DRAFT_CREATED')
        logger.info(f"파이프라인 ID {pipeline_id}: 작성자 단계 완료")

        # Step 2: 편집자
        editor_revision = run_ai_agent(model, "편집자", EDITOR_PROMPT.format(draft_content=creator_draft))
        update_pipeline_step(conn, pipeline_id, editor_revision=editor_revision, status='EDITED')
        logger.info(f"파이프라인 ID {pipeline_id}: 편집자 단계 완료")

        # Step 3: 최종결정자
        decider_prompt = DECIDER_PROMPT.format(
            edited_content=editor_revision,
            existing_articles_list=str(published_tools),
            **selected_tool
        )
        decider_judgment = run_ai_agent(model, "최종결정자", decider_prompt, is_json_output=True)
        update_pipeline_step(conn, pipeline_id, decider_judgment_json=json.dumps(decider_judgment, ensure_ascii=False))
        logger.info(f"파이프라인 ID {pipeline_id}: 최종결정자 단계 완료")

        # 4. 최종 결정에 따른 후처리
        if decider_judgment.get('decision') == '승인':
            article_meta_data['title'] = decider_judgment.get('final_title', article_meta_data['title'])
            save_approved_article(conn, pipeline_id, selected_tool['name'], editor_revision, article_meta_data)
            logger.info(f"파이프라인 ID {pipeline_id}: 콘텐츠 승인 및 저장 완료")
        else:
            reason = decider_judgment.get('reason', '사유 없음')
            update_pipeline_step(conn, pipeline_id, status='AI_REJECTED', rejection_reason=reason)
            logger.info(f"파이프라인 ID {pipeline_id}: 콘텐츠 반려됨. 사유: {reason}")
            print(f"\n🤖 AI 최종결정자가 콘텐츠를 '반려'했습니다. 사유: {reason}")
        
        return 'SUCCESS'
    except Exception as e:
        logger.error(f"파이프라인 실행 중 오류 발생: {str(e)}", exc_info=True)
        raise

def main():
    """
    프로그램의 진입점(Entry Point).
    파이프라인을 실행하고 최종 예외를 처리합니다.
    """
    conn = db_connect()
    try:
        gemini_model = setup_gemini()
        run_pipeline(conn, gemini_model)

    except PipelineError as e:
        error_msg = f"파이프라인 중단: {e}"
        logger.error(error_msg)
        print(f"\n[파이프라인 중단] {e}")
    
    except Exception as e:
        error_msg = f"알 수 없는 치명적 오류 발생: {str(e)}"
        logger.critical(error_msg, exc_info=True)
        print(f"\n[알 수 없는 치명적 오류 발생] {e}")

    finally:
        if conn:
            conn.close()
            print("\n데이터베이스 연결이 종료되었습니다.")

if __name__ == "__main__":
    main()


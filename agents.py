# agents.py
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

class PipelineError(Exception):
    """파이프라인 실행 중 오류 발생 시 사용할 사용자 정의 예외"""
    pass

def setup_gemini():
    """Gemini API 클라이언트를 설정하고 모델을 반환합니다."""
    try:
        genai.configure(api_key=API_KEY)
        # 사용하시는 환경에 맞춰 모델명을 확인해주세요.
        return genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        raise PipelineError(f"❌ Gemini 설정 오류: {e}")

def run_ai_agent(model, agent_name, prompt, is_json_output=False):
    """
    모든 AI Agent의 API 호출을 처리하는 단일 범용 함수.
    실패 시 PipelineError를 발생시킵니다.
    """
    print(f"\n[AGENT: {agent_name}] 작업을 시작합니다...")
    try:
        config = {"response_mime_type": "application/json"} if is_json_output else {}
        response = model.generate_content(prompt, generation_config=config)
        result = json.loads(response.text) if is_json_output else response.text
        if not result:
            raise PipelineError("결과물이 비어 있습니다.")
        print("✅ 작업 완료!")
        return result
    except Exception as e:
        raise PipelineError(f"'{agent_name}' Agent 실행 중 오류 발생: {e}")
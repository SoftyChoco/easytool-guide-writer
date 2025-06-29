# agents.py
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import re

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

def sanitize_json_string(json_str):
    """
    JSON 문자열에서 제어 문자와 유효하지 않은 문자를 제거하여 유효한 JSON 문자열로 변환합니다.
    """
    if not json_str:
        return json_str
    
    # 허용된 제어 문자: \b, \t, \n, \f, \r
    allowed_escapes = ['\b', '\t', '\n', '\f', '\r']
    
    # 문자열 내 모든 제어 문자를 처리
    result = ""
    i = 0
    while i < len(json_str):
        if json_str[i] in ['\b', '\t', '\n', '\f', '\r']:
            # 허용된 이스케이프 시퀀스는 유지
            result += json_str[i]
        elif ord(json_str[i]) < 32 or ord(json_str[i]) == 127:
            # 기타 제어 문자는 제거
            pass
        else:
            result += json_str[i]
        i += 1
    
    # 특수 케이스: JSON 내 이스케이프되지 않은 제어 문자 처리
    result = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', result)
    
    # 유효하지 않은 유니코드 이스케이프 시퀀스 처리
    try:
        # 이 단계에서 문자열이 유효한지 확인
        json.loads(result)
        return result
    except json.JSONDecodeError as e:
        # 여전히 문제가 있는 경우, 더 강력한 정리 시도
        try:
            # 모든 내용을 문자열로 취급하고 다시 직렬화
            parsed = json.loads(result.replace('\\"', '"').replace('\\', '\\\\'))
            return json.dumps(parsed)
        except:
            # 마지막 시도: 문제가 있는 부분을 모두 제거
            return re.sub(r'[^\x20-\x7E\t\n\r]', '', result)

def run_ai_agent(model, agent_name, prompt, is_json_output=False):
    """
    모든 AI Agent의 API 호출을 처리하는 단일 범용 함수.
    실패 시 PipelineError를 발생시킵니다.
    """
    print(f"\n[AGENT: {agent_name}] 작업을 시작합니다...")
    try:
        config = {"response_mime_type": "application/json"} if is_json_output else {}
        response = model.generate_content(prompt, generation_config=config)
        
        if is_json_output:
            # JSON 응답의 경우 제어 문자 제거 후 파싱
            response_text = response.text
            
            # 응답이 JSON으로 시작하지 않는 경우 처리
            if not response_text.strip().startswith('{'):
                # JSON 블록 찾기
                json_match = re.search(r'({[\s\S]*})', response_text)
                if json_match:
                    response_text = json_match.group(1)
            
            sanitized_text = sanitize_json_string(response_text)
            
            try:
                result = json.loads(sanitized_text)
            except json.JSONDecodeError as e:
                # JSON 파싱 실패 시 디버깅 정보 출력
                print(f"JSON 파싱 실패: {e}")
                print(f"원본 텍스트 일부: {response_text[:100]}...")
                
                # 마지막 시도: 문자열을 완전히 정리
                try:
                    # 모든 제어 문자 및 특수 문자 제거
                    clean_text = re.sub(r'[^\x20-\x7E]', '', response_text)
                    result = json.loads(clean_text)
                except Exception:
                    raise PipelineError(f"AI 응답을 JSON으로 파싱할 수 없습니다: {e}")
        else:
            result = response.text
            
        if not result:
            raise PipelineError("결과물이 비어 있습니다.")
        print("✅ 작업 완료!")
        return result
    except Exception as e:
        raise PipelineError(f"'{agent_name}' Agent 실행 중 오류 발생: {e}")
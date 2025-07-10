# agents.py
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import re
import logging
import traceback

# 로깅 설정
logging.basicConfig(
    filename='easytool_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('easytool')

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
        logger.error(f"Gemini 설정 오류: {str(e)}", exc_info=True)
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
    
    # 잘못된 이스케이프 시퀀스 수정 (예: \x, \e 등 JSON에서 허용되지 않는 이스케이프)
    # JSON에서 허용되는 이스케이프 시퀀스: \" \\ \/ \b \f \n \r \t \uXXXX
    result = re.sub(r'\\([^"\\/' + 'bfnrtu])', r'\1', result)
    
    # 유효하지 않은 유니코드 이스케이프 시퀀스 처리
    try:
        # 이 단계에서 문자열이 유효한지 확인
        json.loads(result)
        return result
    except json.JSONDecodeError as e:
        # 로깅: 첫 번째 정리 시도 실패
        logger.error(f"JSON 정리 첫 번째 시도 실패: {str(e)}")
        logger.debug(f"문제가 있는 JSON 문자열 샘플: {result[:200]}")
        
        # 여전히 문제가 있는 경우, 더 강력한 정리 시도
        try:
            # 모든 내용을 문자열로 취급하고 다시 직렬화
            parsed = json.loads(result.replace('\\"', '"').replace('\\', '\\\\'))
            return json.dumps(parsed)
        except Exception as e2:
            # 로깅: 두 번째 정리 시도 실패
            logger.error(f"JSON 정리 두 번째 시도 실패: {str(e2)}")
            
            # 마지막 시도: 문제가 있는 부분을 모두 제거
            return re.sub(r'[^\x20-\x7E\t\n\r]', '', result)

def fix_invalid_escapes(json_str):
    """
    JSON에서 허용되지 않는 이스케이프 시퀀스를 수정합니다.
    특히 'Invalid escape' 오류를 해결하기 위한 함수입니다.
    """
    if not json_str:
        return json_str
    
    # JSON에서 허용되는 이스케이프 시퀀스: \" \\ \/ \b \f \n \r \t \uXXXX
    # 문자열을 순회하며 잘못된 이스케이프 시퀀스를 찾아 수정
    result = ""
    i = 0
    while i < len(json_str):
        # 백슬래시를 발견한 경우
        if json_str[i] == '\\' and i + 1 < len(json_str):
            next_char = json_str[i + 1]
            # 허용된 이스케이프 시퀀스인 경우
            if next_char in '"\\/' + 'bfnrtu':
                result += json_str[i:i+2]  # 백슬래시와 다음 문자 유지
                i += 2
            # 유니코드 이스케이프 시퀀스인 경우 (\uXXXX)
            elif next_char == 'u' and i + 5 < len(json_str):
                # 4자리 16진수 확인
                if all(c in '0123456789abcdefABCDEF' for c in json_str[i+2:i+6]):
                    result += json_str[i:i+6]  # 유효한 유니코드 이스케이프
                    i += 6
                else:
                    # 유효하지 않은 유니코드 이스케이프는 백슬래시 제거
                    result += json_str[i+1]
                    i += 2
            else:
                # 허용되지 않는 이스케이프 시퀀스는 백슬래시 제거
                result += next_char
                i += 2
        else:
            result += json_str[i]
            i += 1
    
    return result

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
                else:
                    logger.warning(f"JSON 블록을 찾을 수 없음: {response_text[:100]}...")
            
            # 잘못된 이스케이프 시퀀스 수정 (첫 번째 시도)
            response_text = fix_invalid_escapes(response_text)
            
            sanitized_text = sanitize_json_string(response_text)
            
            try:
                result = json.loads(sanitized_text)
            except json.JSONDecodeError as e:
                # JSON 파싱 실패 시 디버깅 정보 출력 및 로깅
                error_msg = f"JSON 파싱 실패: {e}"
                print(error_msg)
                print(f"원본 텍스트 일부: {response_text[:100]}...")
                
                # 로그에 더 자세한 정보 기록
                logger.error(error_msg)
                
                # 문제가 발생한 위치 주변의 문자열 로깅 (오류 위치 전후 50자)
                error_pos = e.pos
                start_pos = max(0, error_pos - 50)
                end_pos = min(len(response_text), error_pos + 50)
                context = response_text[start_pos:end_pos]
                
                logger.error(f"파싱 오류 위치: {e.lineno}행 {e.colno}열 (문자 위치: {e.pos})")
                logger.error(f"문제 문자 주변 컨텍스트: {context}")
                logger.error(f"전체 응답 텍스트 길이: {len(response_text)} 문자")
                
                # 이스케이프 문자 분석
                escape_positions = [(m.start(), m.group()) for m in re.finditer(r'\\[^"\\/' + 'bfnrtu]', sanitized_text)]
                if escape_positions:
                    logger.error(f"잘못된 이스케이프 시퀀스 발견: {escape_positions}")
                
                # 마지막 시도: 문자열을 완전히 정리
                try:
                    # 모든 제어 문자 제거
                    clean_text = re.sub(r'[^\x20-\x7E]', '', response_text)
                    
                    # 잘못된 이스케이프 시퀀스 수정
                    clean_text = fix_invalid_escapes(clean_text)
                    
                    result = json.loads(clean_text)
                    logger.info("최종 정리 시도로 JSON 파싱 성공")
                except Exception as final_e:
                    logger.critical(f"모든 JSON 파싱 시도 실패: {final_e}")
                    logger.debug(f"최종 정리 시도 실패한 텍스트: {clean_text[:200]}")
                    
                    # 마지막 수단: 모든 백슬래시를 이중 백슬래시로 변경 후 시도
                    try:
                        escaped_text = response_text.replace('\\', '\\\\')
                        # 이중 백슬래시를 다시 단일 백슬래시로 변환
                        valid_escapes = '"\\/' + 'bfnrtu'
                        for char in valid_escapes:
                            escaped_text = escaped_text.replace('\\\\' + char, '\\' + char)
                        result = json.loads(escaped_text)
                        logger.info("백슬래시 이스케이프 처리 후 JSON 파싱 성공")
                    except Exception:
                        # 정확한 오류 위치와 내용을 로그에 기록
                        if isinstance(e, json.JSONDecodeError):
                            logger.critical(f"JSON 파싱 최종 실패 - 오류 위치: 행 {e.lineno}, 열 {e.colno}, 위치 {e.pos}")
                            if e.pos < len(response_text):
                                # 오류 발생 지점의 문자와 그 주변 문자열 기록
                                error_char = response_text[e.pos] if e.pos < len(response_text) else "문자열 끝"
                                logger.critical(f"오류 발생 문자: '{error_char}' (ASCII: {ord(error_char) if e.pos < len(response_text) else 'N/A'})")
                        
                        raise PipelineError(f"AI 응답을 JSON으로 파싱할 수 없습니다: {e}")
        else:
            result = response.text
            
        if not result:
            logger.error("AI 응답 결과가 비어 있음")
            raise PipelineError("결과물이 비어 있습니다.")
        print("✅ 작업 완료!")
        return result
    except Exception as e:
        logger.error(f"'{agent_name}' Agent 실행 중 오류 발생: {str(e)}", exc_info=True)
        raise PipelineError(f"'{agent_name}' Agent 실행 중 오류 발생: {e}")

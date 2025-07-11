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

# .env 파일에서 환경 변수를 로드하고 기존 환경 변수를 덮어씁니다.
load_dotenv(override=True)
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

def fix_missing_commas(json_str):
    """
    JSON 문자열에서 누락된 콤마를 감지하고 수정합니다.
    특히 'Expecting ',' delimiter' 오류를 해결하기 위한 함수입니다.
    """
    # 객체 내에서 누락된 콤마 수정 (속성 사이)
    # 예: {"a": 1 "b": 2} -> {"a": 1, "b": 2}
    json_str = re.sub(r'(\d+|true|false|null|"[^"]*")\s*("[\w\s]+"\s*:)', r'\1, \2', json_str)
    
    # 배열 내에서 누락된 콤마 수정 (요소 사이)
    # 예: [1 2 3] -> [1, 2, 3]
    json_str = re.sub(r'(\d+|true|false|null|"[^"]*")\s+(\d+|true|false|null|")', r'\1, \2', json_str)
    
    return json_str

def run_ai_agent(model, agent_name, prompt, is_json_output=False):
    """
    모든 AI Agent의 API 호출을 처리하는 단일 범용 함수.
    실패 시 PipelineError를 발생시킵니다.
    """
    # 시작 메시지 출력 제거 (main.py에서 출력함)
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
            
            # 누락된 콤마 수정 (새로 추가)
            response_text = fix_missing_commas(response_text)
            
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
                    
                    # 누락된 콤마 수정 (새로 추가)
                    clean_text = fix_missing_commas(clean_text)
                    
                    # 따옴표 정리 (새로 추가)
                    # 중첩된 따옴표 문제 해결 시도
                    clean_text = re.sub(r'(?<!\\)\\{2,}"', '\\"', clean_text)
                    
                    # 중괄호와 대괄호 균형 확인 및 수정 (새로 추가)
                    open_braces = clean_text.count('{')
                    close_braces = clean_text.count('}')
                    if open_braces > close_braces:
                        clean_text += '}' * (open_braces - close_braces)
                    elif close_braces > open_braces:
                        clean_text = '{' * (close_braces - open_braces) + clean_text
                    
                    open_brackets = clean_text.count('[')
                    close_brackets = clean_text.count(']')
                    if open_brackets > close_brackets:
                        clean_text += ']' * (open_brackets - close_brackets)
                    elif close_brackets > open_brackets:
                        clean_text = '[' * (close_brackets - open_brackets) + clean_text
                    
                    # 마지막 속성 뒤에 콤마가 있으면 제거 (새로 추가)
                    clean_text = re.sub(r',\s*}', '}', clean_text)
                    clean_text = re.sub(r',\s*]', ']', clean_text)
                    
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
                        
                        # 새로 추가: 더 강력한 정규식 기반 JSON 정리
                        # 1. 모든 속성 이름에 따옴표 추가
                        escaped_text = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', escaped_text)
                        
                        # 2. 누락된 콤마 수정 (다시 시도)
                        escaped_text = fix_missing_commas(escaped_text)
                        
                        # 3. 중괄호와 대괄호 균형 다시 확인
                        open_braces = escaped_text.count('{')
                        close_braces = escaped_text.count('}')
                        if open_braces > close_braces:
                            escaped_text += '}' * (open_braces - close_braces)
                        
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
                        
                        # 최후의 수단: 모델에게 다시 요청하기
                        try:
                            # 원본 응답에 문제가 있으므로 모델에게 JSON 형식으로 다시 정리해달라고 요청
                            fix_prompt = f"""
                            다음 텍스트를 유효한 JSON으로 수정해주세요. 특히 콤마 누락, 따옴표 불일치 등의 문제를 해결해주세요:
                            
                            {response_text}
                            
                            수정된 JSON만 반환해주세요. 다른 설명은 필요 없습니다.
                            """
                            
                            fix_response = model.generate_content(fix_prompt)
                            fixed_json = fix_response.text.strip()
                            
                            # 응답에서 JSON 블록 추출
                            json_match = re.search(r'({[\s\S]*})', fixed_json)
                            if json_match:
                                fixed_json = json_match.group(1)
                            
                            # 수정된 JSON 파싱 시도
                            result = json.loads(fixed_json)
                            logger.info("모델을 통한 JSON 수정 후 파싱 성공")
                        except Exception as model_fix_error:
                            logger.critical(f"모델을 통한 JSON 수정 시도도 실패: {model_fix_error}")
                            raise PipelineError(f"AI 응답을 JSON으로 파싱할 수 없습니다: {e}")
        else:
            result = response.text
            
        if not result:
            logger.error("AI 응답 결과가 비어 있음")
            raise PipelineError("결과물이 비어 있습니다.")
        # 완료 메시지도 삭제 (main.py에서만 표시)
        return result
    except Exception as e:
        logger.error(f"'{agent_name}' Agent 실행 중 오류 발생: {str(e)}", exc_info=True)
        raise PipelineError(f"'{agent_name}' Agent 실행 중 오류 발생: {e}")

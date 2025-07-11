import json
import requests # URL 요청을 위해 requests 사용
from agents import PipelineError  # PipelineError 예외 클래스 import

# 기본 URL 구조
BASE_FEATURES_URL = "https://easytool.run/features/{}.json"

def get_features_url(locale='ko'):
    """언어에 따라 알맞은 기능 명세 URL을 반환합니다."""
    return BASE_FEATURES_URL.format(locale)

def fetch_features_from_url(locale='ko'):
    """지정된 언어로 기능 명세 JSON을 불러옵니다."""
    url = get_features_url(locale)
    print(f"🌐 {url} 에서 {locale} 언어의 최신 기능 명세를 불러옵니다...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        features_data = response.json()

        if 'features' not in features_data or not isinstance(features_data['features'], list):
            raise PipelineError("JSON 포맷 오류: 'features' 키가 없거나 리스트 형태가 아닙니다.")

        print("✅ 기능 명세 로딩 완료!")
        return features_data['features']

    except requests.exceptions.RequestException as e:
        raise PipelineError(f"네트워크 오류: 기능 명세를 불러올 수 없습니다. {e}")
    except json.JSONDecodeError:
        raise PipelineError("JSON 파싱 오류: 응답이 유효한 JSON 형식이 아닙니다.")

# 이전 코드는 삭제
# FEATURES_TEXT = """
#"""

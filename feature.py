import json

FEATURES_URL = "https://easytool.run/features.json"

# FEATURES_JSON = fetch_features_from_url(FEATURES_URL)

FEATURES_TEXT = """
{
  "features": [
    {
      "endpoint": "/aes/text",
      "name": "AES 암호화/복호화",
      "description": "텍스트를 안전하게 암호화하고 복호화할 수 있는 도구입니다. 다양한 암호화 모드(CBC, ECB, CFB, OFB, CTR)를 지원하며, 암호화 키 생성 및 관리 기능을 제공합니다. 암호화된 데이터는 JSON 형식으로 저장되어 IV와 모드 정보를 함께 보관합니다.",
      "targetAudience": "general"
    },
    {
      "endpoint": "/base64/text",
      "name": "Base64 변환기",
      "description": "텍스트를 Base64로 인코딩하거나 Base64를 텍스트로 디코딩하는 도구입니다. 한글 등 유니코드 문자를 지원하며, 인코딩/디코딩 결과를 즉시 확인하고 복사할 수 있습니다.",
      "targetAudience": "general"
    },
    {
      "endpoint": "/cron/convert",
      "name": "크론 표현식 변환기",
      "description": "크론(Cron) 표현식을 사람이 이해하기 쉬운 설명으로 변환하거나, 쉽게 크론 표현식을 생성할 수 있는 도구입니다. 다양한 패턴의 랜덤 크론 표현식 자동 생성 기능도 제공합니다.",
      "targetAudience": "developers"
    },
    {
      "endpoint": "/formatter/json",
      "name": "JSON 포매터",
      "description": "JSON 문자열을 예쁘게 포맷팅하거나 압축할 수 있는 도구입니다. 들여쓰기 크기 조정, 파일 업로드/다운로드, 클립보드 복사 기능을 제공합니다.",
      "targetAudience": "general"
    },
    {
      "endpoint": "/formatter/sql",
      "name": "SQL 포매터",
      "description": "SQL 쿼리를 보기 좋게 포맷팅하거나 압축할 수 있는 도구입니다. 다양한 SQL 방언(MySQL, PostgreSQL, T-SQL 등)과 들여쓰기 옵션을 지원합니다.",
      "targetAudience": "developers"
    },
    {
      "endpoint": "/image/ico",
      "name": "파비콘 생성기",
      "description": "이미지를 다양한 크기의 파비콘으로 변환하고 favicon.ico, manifest.json을 포함한 ZIP 파일로 다운로드할 수 있는 도구입니다. 배경색 설정과 투명도 옵션을 제공합니다.",
      "targetAudience": "general"
    },
    {
      "endpoint": "/image/low",
      "name": "이미지 저용량 변환",
      "description": "이미지 화질은 유지하면서 파일 크기를 줄여 저용량으로 변환하는 도구입니다. 품질 조절, 최대 파일 크기 설정, JPG 형식 변환 옵션을 제공합니다.",
      "targetAudience": "general"
    },
    {
      "endpoint": "/image/placehold",
      "name": "이미지 플레이스홀더 생성기",
      "description": "웹 개발 및 디자인용 플레이스홀더 이미지를 생성하는 도구입니다. 크기, 배경색, 텍스트 색상, 포맷(SVG, PNG, JPEG) 등을 설정할 수 있습니다.",
      "targetAudience": "general"
    },
    {
      "endpoint": "/pdf/docx",
      "name": "Word를 PDF로 변환",
      "description": "Microsoft Word(DOCX) 파일을 PDF로 변환하는 도구입니다. 서버 측에서 변환 작업을 수행하며 변환된 PDF를 다운로드할 수 있습니다.",
      "targetAudience": "general"
    },
    {
      "endpoint": "/pdf/pptx",
      "name": "PowerPoint를 PDF로 변환",
      "description": "Microsoft PowerPoint(PPTX) 파일을 PDF로 변환하는 도구입니다. 서버 측에서 변환 작업을 수행하며 변환된 PDF를 다운로드할 수 있습니다.",
      "targetAudience": "general"
    },
    {
      "endpoint": "/pdf/xlsx",
      "name": "Excel을 PDF로 변환",
      "description": "Microsoft Excel(XLSX) 파일을 PDF로 변환하는 도구입니다. 서버 측에서 변환 작업을 수행하며 변환된 PDF를 다운로드할 수 있습니다.",
      "targetAudience": "general"
    },
    {
      "endpoint": "/qrcode",
      "name": "QR코드 생성기",
      "description": "텍스트, URL 등의 정보를 담은 QR코드를 생성하는 도구입니다. QR코드 크기, 색상 등을 설정할 수 있으며 생성된 QR코드를 이미지로 다운로드할 수 있습니다.",
      "targetAudience": "general"
    },
    {
      "endpoint": "/save/text",
      "name": "텍스트 저장 및 공유",
      "description": "텍스트를 온라인에 저장하고 고유 URL을 통해 공유할 수 있는 도구입니다. 저장된 텍스트는 ID를 통해 나중에 접근할 수 있으며, 텍스트 파일로 다운로드할 수도 있습니다.",
      "targetAudience": "general"
    },
    {
      "endpoint": "/text/byte-length",
      "name": "텍스트 바이트 길이 계산기",
      "description": "텍스트의 바이트 길이를 다양한 인코딩(UTF-8, UTF-16, ASCII 등)에 따라 계산하는 도구입니다. 각 인코딩별 바이트 크기를 비교하여 보여줍니다.",
      "targetAudience": "developers"
    },
    {
      "endpoint": "/text/length",
      "name": "텍스트 길이 계산기",
      "description": "텍스트의 문자 수, 단어 수, 줄 수 등 다양한 통계 정보를 제공하는 도구입니다. 공백 포함/제외 문자 수도 함께 계산합니다.",
      "targetAudience": "general"
    },
    {
      "endpoint": "/text/random",
      "name": "랜덤 텍스트 생성기",
      "description": "무작위 텍스트, 비밀번호, 코드 등을 생성하는 도구입니다. 길이, 포함할 문자 유형 등을 설정할 수 있으며 생성된 텍스트의 강도를 평가합니다.",
      "targetAudience": "general"
    },
    {
      "endpoint": "/time/server",
      "name": "서버 시간 확인",
      "description": "서버의 현재 시간을 다양한 형식(Unix 타임스탬프, ISO 8601, UTC 등)으로 확인할 수 있는 도구입니다. 타임존 정보와 함께 제공되며 시간 정보를 복사할 수 있습니다.",
      "targetAudience": "general"
    },
    {
      "endpoint": "/time/unix",
      "name": "유닉스 타임스탬프 변환기",
      "description": "유닉스 타임스탬프와 일반 날짜/시간 형식 간의 변환을 제공하는 도구입니다. 현재 시간 사용 및 타임존 설정 기능을 제공합니다.",
      "targetAudience": "general"
    },
    {
      "endpoint": "/urlencode",
      "name": "URL 인코딩/디코딩",
      "description": "URL에 사용되는 문자열을 인코딩하거나 디코딩하는 도구입니다. 특수문자, 유니코드 문자 등을 URL 안전한 형식으로 변환하거나 원래 형태로 복원합니다.",
      "targetAudience": "general"
    },
    {
      "endpoint": "/zip",
      "name": "ZIP 압축/해제",
      "description": "파일과 폴더를 ZIP 형식으로 압축하거나 ZIP 파일을 해제하는 도구입니다. 다중 파일 선택 및 폴더 구조 유지 기능을 제공합니다.",
      "targetAudience": "general"
    }
  ]
} 
"""

FEATURES_JSON = json.loads(FEATURES_TEXT)['features']

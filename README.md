# EasyTool Guide Writer

EasyTool Guide Writer는 [EasyTool.run](https://easytool.run)의 기능 가이드를 자동으로 작성해주는 AI 기반 콘텐츠 생성 파이프라인입니다. Google Gemini API를 활용하여 **무료**로 고품질의 기술 가이드를 생성, 편집, 검증하는 자동화된 시스템입니다.

> **마음대로 수정해서 사용하셔도 되지만, 도움이 되셨다면 또 다른 사람에게 도움을 전해주세요!** 💖

## AI 생성 콘텐츠 표시

이 프로젝트로 생성된 모든 콘텐츠에는 다음과 같은 문구를 포함하는 것을 권장합니다:

```
* 이 글은 AI가 자동으로 작성하였습니다.
```

AI가 작성한 콘텐츠와 사람이 작성한 콘텐츠를 구분하는 것은 다음과 같은 이유로 중요합니다:
- 콘텐츠의 출처 투명성 제공
- 사용자에게 정보의 생성 방식에 대한 명확한 이해 제공
- 향후 AI 콘텐츠에 대한 규제 준수
- 윤리적인 AI 활용 촉진

## 프로젝트 개요

이 프로젝트는 다음과 같은 세 가지 AI 에이전트를 활용하여 콘텐츠 생성 파이프라인을 구성합니다:

1. **작성자(Creator)**: 초기 콘텐츠 초안을 작성합니다.
2. **편집자(Editor)**: 초안을 검토하고 가독성을 개선합니다.
3. **최종결정자(Decider)**: 콘텐츠의 사실 관계와 품질을 검증하여 발행 여부를 결정합니다.

생성된 콘텐츠는 SQLite 데이터베이스에 저장되며, 중복 콘텐츠 방지 및 작업 기록 관리 기능을 제공합니다.

## 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/yourusername/easytool-guide-writer.git
cd easytool-guide-writer
```

### 2. 필요 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 Google Gemini API 키를 추가합니다:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

Google Gemini API 키는 [Google AI Studio](https://aistudio.google.com/apikey)에서 발급받을 수 있습니다. Gemini 2.5 Flash 모델은 일정량까지 무료로 제공됩니다. 자세한 가격 정보는 [Gemini API 가격 책정 페이지](https://ai.google.dev/gemini-api/docs/pricing?hl=ko#gemini-2.5-flash)에서 확인할 수 있습니다.

### 4. 데이터베이스 초기화

```bash
python setup.py
```

## 시스템 요구사항

- **Python 버전**: 이 프로젝트는 Python 3.12에서 개발 및 테스트되었습니다.
- **운영체제**: Windows, macOS, Linux에서 실행 가능합니다.

## 사용 방법

### 1. 프로그램 실행

```bash
python main.py
```

### 2. 작동 방식

프로그램이 실행되면 다음과 같은 순서로 작동합니다:

1. `feature.py`에 정의된 EasyTool.run의 기능 목록에서 아직 가이드가 작성되지 않은 기능을 선택합니다.
2. 작성자(Creator) 에이전트가 초기 콘텐츠 초안을 작성합니다.
3. 편집자(Editor) 에이전트가 초안을 검토하고 개선합니다.
4. 최종결정자(Decider) 에이전트가 콘텐츠의 품질과 사실 관계를 검증합니다.
5. 승인된 콘텐츠는 데이터베이스에 저장되며, 반려된 콘텐츠는 사유와 함께 기록됩니다.

### 3. 결과 확인

생성된 콘텐츠는 `easytool_content.db` SQLite 데이터베이스에 저장됩니다. 다음 명령어로 데이터베이스를 확인할 수 있습니다:

```bash
sqlite3 easytool_content.db
```

SQLite 쉘에서 다음과 같은 쿼리를 실행하여 생성된 콘텐츠를 확인할 수 있습니다:

```sql
SELECT id, tool_name, title FROM articles;
```

특정 콘텐츠의 내용을 확인하려면:

```sql
SELECT content_markdown FROM articles WHERE id = 1;
```

## 프로젝트 구조

```
easytool-guide-writer/
  ├── agents.py         # AI 에이전트 설정 및 실행 관련 코드
  ├── db_handler.py     # 데이터베이스 연결 및 쿼리 처리
  ├── feature.py        # EasyTool.run 기능 목록 정의
  ├── main.py           # 메인 실행 파일
  ├── prompts/          # AI 에이전트용 프롬프트
  │   ├── creator.md    # 작성자 에이전트 프롬프트
  │   ├── decider.md    # 최종결정자 에이전트 프롬프트
  │   └── editor.md     # 편집자 에이전트 프롬프트
  ├── README.md         # 프로젝트 설명
  ├── requirements.txt  # 필요 패키지 목록
  └── setup.py          # 데이터베이스 초기화 스크립트
```

## 커스터마이징

### 프롬프트 수정

`prompts/` 디렉토리의 마크다운 파일을 수정하여 각 AI 에이전트의 작업 방식을 조정할 수 있습니다:

- `creator.md`: 초기 콘텐츠 작성 지침
- `editor.md`: 콘텐츠 편집 지침
- `decider.md`: 콘텐츠 검증 및 승인 기준

### 기능 목록 수정

`feature.py` 파일의 `FEATURES_JSON` 변수를 수정하여 작성할 가이드 목록을 변경할 수 있습니다.

## 문제 해결

### API 키 오류

"❌ Gemini 설정 오류" 메시지가 표시되면 `.env` 파일에 올바른 API 키가 설정되었는지 확인하세요.

### 콘텐츠 생성 오류

특정 단계에서 오류가 발생하면 해당 단계의 프롬프트를 확인하고 필요에 따라 수정하세요.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

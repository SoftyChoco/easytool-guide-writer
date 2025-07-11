# EasyTool Guide Writer ✨

안녕하세요! EasyTool Guide Writer는 [EasyTool.run](https://easytool.run)의 기능 가이드를 쉽고 빠르게 만들어주는 간단한 프로젝트예요. Google Gemini API를 활용해서 **무료로** 가이드를 자동으로 만들 수 있어요!

> **마음껏 수정해서 사용하시고, 도움이 되셨다면 다른 분들에게도 알려주세요!** 💖

## AI 작성 표시하기

이걸 통해 만든 컨텐츠에는 아래와 같이 입력해주시면 좋을 것 같아요.

```
* 이 글은 AI가 자동으로 작성하였습니다.
```

## 이 프로젝트는요...

세 가지의 역할의 프롬프트로 만들어요:

1. **작성자**: 처음 글을 써요 ✍️
2. **편집자**: 글을 다듬어요 🖋️
3. **최종결정자**: 내용이 정확한지 확인해요 🔍

만들어진 글은 데이터베이스에 깔끔하게 저장되고, 중복된 내용은 알아서 걸러줘요!

## 주요 기능 ✨

- **다국어 지원**: 한국어(ko)와 영어(en) 콘텐츠를 모두 생성할 수 있어요!
- **강력한 JSON 파싱**: 오류가 발생해도 자동으로 복구하여 파이프라인이 중단되지 않아요!
- **자동화된 콘텐츠 생성**: 작성부터 검토까지 모든 과정이 자동화되어 있어요!

## 시작하기 🚀

### 1. 내려받기

```bash
git clone https://github.com/yourusername/easytool-guide-writer.git
cd easytool-guide-writer
```

### 2. 가상환경 만들기

```bash
# 가상환경 만들기
python -m venv venv

# 가상환경 켜기
# Windows 사용자라면
venv\Scripts\activate
# Mac이나 Linux 사용자라면
source venv/bin/activate
```

### 3. 필요한 것들 설치하기

```bash
pip install -r requirements.txt
```

### 4. API 키 설정하기

프로젝트 폴더에 `.env` 파일을 만들고 이렇게 적어주세요:

```
GOOGLE_API_KEY=여기에_API_키_넣기
```

API 키는 [Google AI Studio](https://aistudio.google.com/apikey)에서 무료로 받을 수 있어요. Gemini 2.5 Flash 모델은 일정량까지 무료랍니다! 자세한 내용은 [가격 안내](https://ai.google.dev/gemini-api/docs/pricing?hl=ko#gemini-2.5-flash)에서 확인하세요.

### 5. 데이터베이스 준비하기

```bash
python setup.py
```

## 필요한 환경

- **Python**: 3.12 버전이면 좋아요 (이 버전만 테스트 해봤어요!)
- **OS**: Windows, Mac, Linux 모두 OK!

## 어떻게 사용하나요? 🤔

### 1. 실행하기

```bash
# 한국어 콘텐츠 생성 (기본값)
python main.py

# 영어 콘텐츠 생성
python main.py --locale en
# 또는 줄여서
python main.py --l en
```

### 2. 작동 과정

실행하면 이런 일이 일어나요:

1. 아직 가이드가 없는 기능을 찾아요
2. 작성자가 초안을 써요
3. 편집자가 글을 더 좋게 만들어요
4. 최종결정자가 내용을 꼼꼼히 확인해요
5. 좋은 글은 저장하고, 아니면 이유와 함께 기록해요

### 3. 결과물 확인하기

만들어진 글은 `easytool_content.db` 파일에 저장돼요. 이렇게 확인할 수 있어요:

```bash
sqlite3 easytool_content.db
```

SQLite에서 이런 명령어로 확인해보세요:

```sql
SELECT id, tool_name, title, locale FROM articles;
```

특정 글의 내용이 궁금하다면:

```sql
SELECT content_markdown FROM articles WHERE id = 1;
```

## 파일 구성 📁

```
easytool-guide-writer/
  ├── agents.py         # AI 친구들 관련 코드
  ├── db_handler.py     # 데이터베이스 관리
  ├── feature.py        # 기능 목록
  ├── main.py           # 메인 실행 파일
  ├── prompts/          # AI 친구들을 위한 지시문
  │   ├── ko/           # 한국어 프롬프트
  │   │   ├── creator.md    # 작성자 지시문
  │   │   ├── decider.md    # 최종결정자 지시문
  │   │   └── editor.md     # 편집자 지시문
  │   └── en/           # 영어 프롬프트
  │       ├── creator.md    # 작성자 지시문
  │       ├── decider.md    # 최종결정자 지시문
  │       └── editor.md     # 편집자 지시문
  ├── README.md         # 지금 읽고 계신 이 파일!
  ├── requirements.txt  # 필요한 패키지 목록
  └── setup.py          # 초기 설정 스크립트
```

## 내 맘대로 바꿔보기 ✏️

### 지시문 수정하기

`prompts/` 폴더의 파일들을 수정해서 AI 친구들의 작업 방식을 바꿀 수 있어요:

- `creator.md`: 어떤 글을 쓸지
- `editor.md`: 어떻게 글을 다듬을지
- `decider.md`: 어떤 기준으로 검토할지

각 언어별로 별도의 폴더(`ko/`, `en/`)에 프롬프트가 있어요!

### 기능 목록 수정하기

`feature.py` 파일의 `fetch_features_from_url` 함수를 통해 각 언어별 기능 목록을 가져와요.

## 문제가 생겼어요! 🛠️

### API 키 문제

"❌ Gemini 설정 오류" 메시지가 나타나면 `.env` 파일에 API 키가 제대로 들어있는지 확인해보세요.

### JSON 파싱 오류

JSON 파싱 오류가 발생해도 걱정하지 마세요! 자동으로 복구하여 파이프라인이 계속 진행됩니다. 만약 계속해서 오류가 발생한다면 `agents.py` 파일의 JSON 파싱 로직을 확인해보세요.

### 글 생성 문제

특정 단계에서 문제가 생기면 해당 단계의 지시문을 살펴보고 필요하다면 수정해보세요.

## 라이선스

이 프로젝트는 MIT 라이선스로 자유롭게 사용하실 수 있어요! 🎉


* 이 README.md는 AI가 자동으로 작성하였습니다. :)
# AI Agent from scratch

Google AI Studio API(Gemini/Gemma)를 사용하는 간단한 대화형 챗봇 프로젝트.

## 기능

- 터미널에서 LLM과 대화하는 루프
- API 키는 환경변수로 관리 (`.env`)
- 대화 히스토리 유지 (chat session)

## 설치

```bash
pip install google-genai python-dotenv
```

## 설정

`.env` 파일을 프로젝트 루트에 생성:

```
GOOGLE_API_KEY=your_api_key_here
```

API 키는 [Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급받을 수 있습니다.

## 실행

```bash
python main.py
```

종료하려면 `exit` 입력.

## 파일

- `main.py` — 메인 챗봇 스크립트
- `list_models.py` — 사용 가능한 모델 목록 출력 유틸리티

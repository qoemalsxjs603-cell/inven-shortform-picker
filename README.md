# 인벤 숏폼 후보 추천기

## 수정 내용

기존 버전은 앱 시작과 동시에 OpenAI Client를 만들면서 Streamlit Secrets를 제대로 읽지 못해 오류가 날 수 있었습니다.

이번 버전은 버튼을 누른 뒤 OpenAI API Key를 확인하도록 수정했습니다.

## 설치

```bash
pip install -r requirements.txt
```

## 로컬 실행

.env 파일에 API Key 입력:

```txt
OPENAI_API_KEY=sk-너의_API_KEY
```

실행:

```bash
streamlit run app.py
```

## Streamlit Cloud 설정

GitHub에는 `.env` 파일을 올리지 마세요.

Streamlit Cloud 앱에서:

1. Manage app
2. Settings
3. Secrets
4. 아래 내용 입력

```toml
OPENAI_API_KEY = "sk-너의_API_KEY"
```

5. 저장 후 앱 재실행

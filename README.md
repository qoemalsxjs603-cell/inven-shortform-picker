# 인벤 숏폼 후보 추천기 - 무료 버전

OpenAI API 없이 작동하는 무료 버전입니다.

## 기능

- 인벤 오픈이슈갤러리 게임 카테고리 글 수집
- 제목 / 댓글 수 / 논란 키워드 기반 점수 계산
- TOP 3 숏폼 후보 추천
- 숏폼 제목, 첫 3초 훅, 간단 구성안 자동 생성

## 설치

```bash
pip install -r requirements.txt
```

## 실행

```bash
streamlit run app.py
```

## Streamlit Cloud 배포

GitHub에 아래 파일만 올리면 됩니다.

- app.py
- requirements.txt
- README.md

API Key나 Secrets 설정은 필요 없습니다.

# 인벤 숏폼 후보 추천기 - 무료 버전 / 공지 제외 버전

OpenAI API 없이 작동하는 무료 버전입니다.

## 수정 내용

- 인벤 오픈이슈갤러리 게임 카테고리에서 글 수집
- 공지 / 안내 / 필독 / 관리자성 글 제외
- 실제 갤러리 글만 대상으로 TOP 3 추천
- API Key 필요 없음
- Streamlit Secrets 설정 필요 없음

## 기능

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

기존 앱을 쓰고 있다면 위 3개 파일을 교체한 뒤 Streamlit에서 Reboot app을 누르세요.

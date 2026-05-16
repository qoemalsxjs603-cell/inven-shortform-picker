import re
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

INVEN_URL = "https://m.inven.co.kr/board/webzine/2097?category=%EA%B2%8C%EC%9E%84"


def crawl_inven():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(INVEN_URL, headers=headers, timeout=10)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    posts = []
    links = soup.select("a[href*='/board/webzine/2097/']")
    seen = set()

    for a in links:
        title = a.get_text(" ", strip=True)
        href = a.get("href")

        if not title or not href:
            continue

        if len(title) < 5:
            continue

        if href in seen:
            continue

        seen.add(href)

        if href.startswith("/"):
            href = "https://m.inven.co.kr" + href

        parent_text = a.parent.get_text(" ", strip=True) if a.parent else ""

        comment_count = 0
        comment_match = re.search(r"\[(\d+)\]", title)
        if comment_match:
            comment_count = int(comment_match.group(1))
            title = re.sub(r"\[\d+\]", "", title).strip()

        posts.append({
            "title": title,
            "url": href,
            "raw_text": parent_text,
            "comments": comment_count
        })

    return posts[:40]


def make_shortform_title(title):
    title_lower = title.lower()

    if any(k in title for k in ["논란", "사과", "민심", "분노", "터짐", "난리"]):
        return f"유저들이 지금 난리난 이유: {title}"

    if any(k in title for k in ["버그", "오류", "서버", "점검"]):
        return f"게임 유저들이 분노한 사건: {title}"

    if any(k in title for k in ["확률", "과금", "가챠", "BM", "패키지"]):
        return f"과금 때문에 말 나오는 이유: {title}"

    if any(k in title for k in ["너프", "상향", "밸런스", "패치"]):
        return f"이번 패치가 논란인 이유: {title}"

    if any(k in title for k in ["섭종", "서비스 종료", "종료"]):
        return f"결국 여기까지 온 게임: {title}"

    return f"지금 게임 커뮤니티에서 주목받는 이슈: {title}"


def make_hook(title):
    if any(k in title for k in ["논란", "민심", "분노", "난리", "터짐"]):
        return "지금 이 게임 유저들 반응이 심상치 않습니다."

    if any(k in title for k in ["사과", "공지"]):
        return "운영진이 결국 입장을 냈습니다."

    if any(k in title for k in ["과금", "확률", "가챠"]):
        return "이번엔 과금 문제로 말이 나오고 있습니다."

    if any(k in title for k in ["버그", "오류", "서버"]):
        return "게임에서 또 예상치 못한 문제가 터졌습니다."

    if any(k in title for k in ["패치", "너프", "밸런스"]):
        return "이번 패치 이후 유저 반응이 갈리고 있습니다."

    return "오늘 인벤에서 눈에 띄는 게임 이슈가 올라왔습니다."


def basic_score(post):
    title = post["title"]
    score = 0

    keyword_scores = {
        "논란": 30,
        "민심": 30,
        "분노": 30,
        "난리": 25,
        "터짐": 25,
        "사과": 25,
        "운영": 22,
        "과금": 22,
        "확률": 22,
        "가챠": 20,
        "BM": 20,
        "너프": 18,
        "밸런스": 18,
        "패치": 15,
        "버그": 20,
        "오류": 18,
        "서버": 15,
        "점검": 12,
        "섭종": 25,
        "서비스 종료": 25,
        "검열": 20,
        "표절": 25,
        "레전드": 15,
        "역대급": 15,
        "실화": 15,
        "망함": 20,
    }

    for keyword, point in keyword_scores.items():
        if keyword in title:
            score += point

    comments = post.get("comments", 0)
    score += comments * 3

    # 제목 길이가 너무 짧거나 너무 길면 숏폼화 점수 약간 감소
    if 10 <= len(title) <= 45:
        score += 10
    elif len(title) > 70:
        score -= 5

    return round(score, 2)


def reason_text(post):
    reasons = []
    title = post["title"]

    if post.get("comments", 0) >= 10:
        reasons.append("댓글 반응이 있어 논쟁형 숏폼으로 만들기 좋음")
    elif post.get("comments", 0) >= 3:
        reasons.append("댓글이 어느 정도 달려 커뮤니티 반응 확인 가능")

    if any(k in title for k in ["논란", "민심", "분노", "난리", "터짐", "사과"]):
        reasons.append("논란/민심 폭발형 키워드 포함")

    if any(k in title for k in ["과금", "확률", "가챠", "BM"]):
        reasons.append("과금·확률 이슈는 유저 감정 반응이 강함")

    if any(k in title for k in ["패치", "너프", "밸런스"]):
        reasons.append("패치/밸런스 이슈는 찬반 댓글 유도에 유리")

    if any(k in title for k in ["버그", "오류", "서버", "점검"]):
        reasons.append("버그/서버 문제는 짧은 사건형 영상으로 만들기 쉬움")

    if not reasons:
        reasons.append("게임 커뮤니티에서 주목할 만한 이슈로 판단됨")

    return " / ".join(reasons)


st.set_page_config(page_title="인벤 숏폼 후보 추천기 무료버전", layout="wide")

st.title("인벤 오픈이슈갤러리 숏폼 후보 추천기")
st.caption("OpenAI API 없이 무료로 작동하는 버전입니다. 게임 카테고리 글을 점수화해 TOP 3를 추천합니다.")

st.info("이 버전은 API Key가 필요 없습니다. 인벤 글 제목, 댓글 수, 논란 키워드를 기준으로 추천합니다.")

if st.button("오늘의 후보 3개 뽑기"):
    with st.spinner("인벤 글 수집 중..."):
        try:
            posts = crawl_inven()
        except Exception as e:
            st.error("인벤 글 수집 중 오류가 발생했습니다.")
            st.exception(e)
            st.stop()

    if not posts:
        st.error("글을 가져오지 못했습니다. 인벤 페이지 구조가 바뀌었을 수 있습니다.")
        st.stop()

    for post in posts:
        post["score"] = basic_score(post)
        post["shortform_title"] = make_shortform_title(post["title"])
        post["hook"] = make_hook(post["title"])
        post["reason"] = reason_text(post)

    ranked_posts = sorted(posts, key=lambda x: x["score"], reverse=True)

    st.subheader("수집된 후보 목록")
    df = pd.DataFrame(ranked_posts)
    st.dataframe(df[["title", "comments", "score", "url"]], use_container_width=True)

    st.subheader("오늘의 TOP 3 추천")

    top3 = ranked_posts[:3]

    for idx, item in enumerate(top3, start=1):
        st.markdown("---")
        st.markdown(f"## {idx}위. {item['shortform_title']}")
        st.write(f"**원본 제목:** {item['title']}")
        st.write(f"**예상 점수:** {item['score']}점")
        st.write(f"**댓글 수:** {item['comments']}개")
        st.write(f"**선정 이유:** {item['reason']}")
        st.write(f"**첫 3초 훅:** {item['hook']}")
        st.markdown(f"[원문 보기]({item['url']})")

        with st.expander("간단 숏폼 구성안"):
            st.markdown(f"""
**0~3초**  
{item['hook']}

**3~15초**  
인벤 오픈이슈갤러리에 올라온 이 글이 주목받고 있습니다.

**15~35초**  
핵심은 `{item['title']}` 입니다.  
댓글 반응과 제목 키워드를 보면 유저들의 관심이 모이고 있습니다.

**35~45초**  
이 이슈가 단순 해프닝인지, 진짜 민심 변화의 신호인지는 조금 더 지켜봐야 합니다.

**마무리**  
여러분은 이 이슈 어떻게 보시나요?
""")

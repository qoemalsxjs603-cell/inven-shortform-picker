import os
import re
import json
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INVEN_URL = "https://m.inven.co.kr/board/webzine/2097?category=%EA%B2%8C%EC%9E%84"


def to_int(text):
    if not text:
        return 0
    text = str(text).replace(",", "").strip()
    match = re.search(r"\d+", text)
    return int(match.group()) if match else 0


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
            "comments": comment_count,
            "views": 0,
            "recommends": 0
        })

    return posts[:30]


def basic_score(post):
    title = post["title"]

    hot_keywords = [
        "논란", "난리", "충격", "분노", "민심", "터짐", "사과",
        "망함", "역대급", "레전드", "실화", "과금", "확률",
        "너프", "버그", "섭종", "검열", "표절", "운영"
    ]

    score = 0

    for keyword in hot_keywords:
        if keyword in title:
            score += 10

    score += post.get("comments", 0) * 2
    score += post.get("recommends", 0) * 3
    score += post.get("views", 0) / 1000

    return round(score, 2)


def ask_ai_top3(posts):
    candidate_text = ""

    for i, post in enumerate(posts, start=1):
        candidate_text += f"""
{i}.
제목: {post['title']}
댓글수: {post['comments']}
기본점수: {post['basic_score']}
링크: {post['url']}
"""

    prompt = f"""
너는 한국 게임 숏폼 채널의 기획자다.

아래 인벤 오픈이슈갤러리 게임 카테고리 글 중에서
조회수가 가장 잘 나올 가능성이 높은 TOP 3를 골라라.

선정 기준:
1. 논란성
2. 충격성
3. 유저 분노/민심 폭발 가능성
4. 댓글을 유도할 수 있는가
5. 30~50초 숏폼으로 만들기 쉬운가
6. 게임 주제와 직접 관련 있는가

반드시 JSON 형식으로만 답해라.

형식:
{{
  "top3": [
    {{
      "rank": 1,
      "title": "글 제목",
      "url": "링크",
      "score": 9.2,
      "reason": "선정 이유",
      "shortform_title": "숏폼 제목",
      "hook": "첫 3초 훅 문장"
    }}
  ]
}}

후보 글:
{candidate_text}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "너는 조회수 중심의 숏폼 콘텐츠 기획 전문가다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    content = response.choices[0].message.content
    return json.loads(content)


st.set_page_config(page_title="인벤 숏폼 후보 추천기", layout="wide")

st.title("인벤 오픈이슈갤러리 숏폼 후보 추천기")
st.caption("게임 카테고리에서 논란/충격/민심 폭발형 소재 TOP 3를 추천합니다.")

if st.button("오늘의 후보 3개 뽑기"):
    with st.spinner("인벤 글 수집 중..."):
        posts = crawl_inven()

    if not posts:
        st.error("글을 가져오지 못했습니다. 인벤 페이지 구조가 바뀌었을 수 있습니다.")
        st.stop()

    for post in posts:
        post["basic_score"] = basic_score(post)

    posts = sorted(posts, key=lambda x: x["basic_score"], reverse=True)[:15]

    st.subheader("1차 수집 후보")
    st.dataframe(pd.DataFrame(posts)[["title", "comments", "basic_score", "url"]])

    with st.spinner("AI가 숏폼 가능성을 평가 중..."):
        result = ask_ai_top3(posts)

    st.subheader("오늘의 TOP 3 추천")

    for item in result["top3"]:
        st.markdown("---")
        st.markdown(f"## {item['rank']}위. {item['shortform_title']}")
        st.write(f"**원본 제목:** {item['title']}")
        st.write(f"**예상 점수:** {item['score']} / 10")
        st.write(f"**선정 이유:** {item['reason']}")
        st.write(f"**첫 3초 훅:** {item['hook']}")
        st.markdown(f"[원문 보기]({item['url']})")

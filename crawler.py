import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# 포함 키워드 (이것 중 하나라도 있으면 수집)
INCLUDE_KEYWORDS = [
    '모집', '프로그램', '행사', '교육', '축제',
    '참가자', '수강생', '신청', '강좌', '체험',
    '문화', '특강', '캠프', '공연', '전시'
]

# 제외 키워드 (이것 중 하나라도 있으면 제외)
EXCLUDE_KEYWORDS = [
    '입찰', '계약', '공사', '채용', '고시',
    '공매', '용역', '구매', '공고문', '고용'
]

# 카테고리 자동 분류
def classify(title):
    if any(k in title for k in ['교육', '강좌', '특강', '수강', '학습']):
        return '교육'
    if any(k in title for k in ['축제', '공연', '전시', '문화']):
        return '축제/문화'
    if any(k in title for k in ['행사', '체험', '캠프', '이벤트']):
        return '행사'
    if any(k in title for k in ['복지', '돌봄', '지원', '서비스']):
        return '복지'
    return '기타'

# 대상 자동 추출
def extract_target(title):
    if any(k in title for k in ['어린이', '아동', '초등']):
        return '어린이'
    if any(k in title for k in ['청소년', '청년']):
        return '청소년/청년'
    if any(k in title for k in ['어르신', '노인', '시니어']):
        return '어르신'
    if any(k in title for k in ['가족', '부모', '엄마', '아빠']):
        return '가족'
    return '전체'

def is_relevant(title):
    if any(k in title for k in EXCLUDE_KEYWORDS):
        return False
    return True


def crawl_guro():
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}

    # 구로구청 고시공고
    url = "https://www.guro.go.kr/www/selectBbsNttList.do?bbsNo=663&key=1791"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.select('table tbody tr')
        for row in rows:
            title_tag = row.select_one('td a')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            if not is_relevant(title):
                continue
            cols = row.select('td')
            date = cols[-1].get_text(strip=True) if cols else ''
            href = title_tag.get('href', '')
            link = "https://www.guro.go.kr" + href if href.startswith('/') else href
            results.append({
                "title": title,
                "link": link,
                "date": date,
                "source": "구로구청",
                "category": classify(title),
                "target": extract_target(title)
            })
    except Exception as e:
        print(f"오류: {e}")

    # 구로구청 소식/행사
    url2 = "https://www.guro.go.kr/www/selectBbsNttList.do?bbsNo=662&key=3477"
    try:
        res = requests.get(url2, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.select('table tbody tr')
        for row in rows:
            title_tag = row.select_one('td a')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            if not is_relevant(title):
                continue
            cols = row.select('td')
            date = cols[-1].get_text(strip=True) if cols else ''
            href = title_tag.get('href', '')
            link = "https://www.guro.go.kr" + href if href.startswith('/') else href
            results.append({
                "title": title,
                "link": link,
                "date": date,
                "source": "구로구청 소식",
                "category": classify(title),
                "target": extract_target(title)
            })
    except Exception as e:
        print(f"오류: {e}")

    output = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "items": results
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"수집 완료: {len(results)}건")

if __name__ == "__main__":
    crawl_guro()

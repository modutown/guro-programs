import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

EXCLUDE_KEYWORDS = [
    '입찰', '계약', '공사', '채용', '고시',
    '공매', '용역', '구매', '고용'
]

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

def make_link(href):
    if href.startswith('http'):
        return href
    return "https://www.guro.go.kr/www/" + href.lstrip('./')

def crawl_board(url, source):
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
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
            if any(k in title for k in EXCLUDE_KEYWORDS):
                continue
            cols = row.select('td')
            date = cols[-1].get_text(strip=True) if cols else ''
            href = title_tag.get('href', '')
            link = make_link(href)
            results.append({
                "title": title,
                "link": link,
                "date": date,
                "source": source,
                "category": classify(title),
                "target": extract_target(title)
            })
    except Exception as e:
        print(f"오류 ({source}): {e}")
    return results

def crawl_guro():
    results = []
    results += crawl_board(
        "https://www.guro.go.kr/www/selectBbsNttList.do?bbsNo=663&key=1791",
        "구로구청"
    )
    results += crawl_board(
        "https://www.guro.go.kr/www/selectBbsNttList.do?bbsNo=662&key=3477",
        "구로구청 소식"
    )
    output = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "items": results
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"수집 완료: {len(results)}건")

if __name__ == "__main__":
    crawl_guro()

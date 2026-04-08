import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def crawl_guro():
    results = []
    
    # 구로구청 고시공고
    url = "https://www.guro.go.kr/www/selectBbsNttList.do?bbsNo=663&key=1791"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        rows = soup.select('table tbody tr')
        for row in rows:
            cols = row.select('td')
            if len(cols) < 3:
                continue
            title_tag = row.select_one('td a')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link_href = title_tag.get('href', '')
            link = "https://www.guro.go.kr" + link_href if link_href.startswith('/') else link_href
            date = cols[-1].get_text(strip=True) if cols else ''
            
            results.append({
                "title": title,
                "link": link,
                "date": date,
                "source": "구로구청 고시공고"
            })
    except Exception as e:
        print(f"오류: {e}")
    
    # 저장
    output = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "items": results
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"수집 완료: {len(results)}건")

if __name__ == "__main__":
    crawl_guro()

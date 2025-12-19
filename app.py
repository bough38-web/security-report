# app.py
import requests
from bs4 import BeautifulSoup
import json
import datetime
import os

# --- 설정 ---
KEYWORDS = ["KT텔레캅", "SK쉴더스", "에스원", "보안 사고", "해킹", "개인정보 유출", "산업 재해"]
OUTPUT_FILE = "index.html"

def get_risk(title):
    t = title.lower()
    if any(x in t for x in ['사망', '유출', '해킹', '화재', '구속']): return 'RED'
    if any(x in t for x in ['주의', '오류', '점검', '취약']): return 'AMBER'
    return 'GREEN'

def crawl():
    print("크롤링 시작...")
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for kw in KEYWORDS:
        try:
            url = f"https://search.naver.com/search.naver?where=news&query={kw}&sort=1"
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            
            for item in soup.select("a.news_tit")[:3]:
                results.append({
                    "keyword": kw,
                    "title": item.get_text(),
                    "link": item['href'],
                    "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "risk": get_risk(item.get_text())
                })
        except: pass
    
    return results if results else [{"keyword": "시스템", "title": "데이터 수집 실패", "link": "#", "date": "-", "risk": "RED"}]

data = crawl()
json_data = json.dumps(data, ensure_ascii=False)

html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-slate-100 p-6">
    <div class="max-w-4xl mx-auto space-y-6">
        <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h1 class="text-2xl font-bold text-slate-800 mb-2">🛡️ Security Daily Watch</h1>
            <p class="text-slate-500 text-sm">자동 업데이트: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3" id="list"></div>
    </div>

    <script>
        const data = {json_data};
        const list = document.getElementById("list");
        
        data.forEach(d => {{
            const el = document.createElement("a");
            el.href = d.link;
            el.target = "_blank";
            el.className = "block bg-white p-5 rounded-xl border border-slate-200 hover:border-blue-500 hover:shadow-md transition-all group";
            el.innerHTML = `
                <div class="flex items-center gap-2 mb-2">
                    <span class="px-2 py-0.5 text-xs font-bold rounded bg-slate-100 text-slate-600">${{d.keyword}}</span>
                    <span class="px-2 py-0.5 text-xs font-bold rounded ${{d.risk === 'RED' ? 'bg-red-100 text-red-600' : d.risk === 'AMBER' ? 'bg-yellow-100 text-yellow-600' : 'bg-green-100 text-green-600'}}">${{d.risk}}</span>
                </div>
                <h3 class="font-bold text-slate-800 group-hover:text-blue-600 leading-snug">${{d.title}}</h3>
                <p class="text-xs text-slate-400 mt-2">${{d.date}}</p>
            `;
            list.appendChild(el);
        }});
    </script>
</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)
print("업데이트 완료")
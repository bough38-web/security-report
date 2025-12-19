# app.py
import requests
from bs4 import BeautifulSoup
import json
import datetime
import os
import base64
import time
import random

# --- [1] 설정 ---
KEYWORDS = ["KT텔레캅", "SK쉴더스", "에스원", "보안 사고", "해킹", "개인정보 유출", "산업 재해"]
OUTPUT_FILE = "index.html"

# --- [2] 봇 차단 우회용 헤더 (사람인 척 위장) ---
def get_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.naver.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

# --- [3] 위험도 분석 ---
def get_risk(title):
    t = title.lower()
    if any(x in t for x in ['사망', '유출', '해킹', '화재', '구속', '긴급', '마비', '충돌', '적발']): return 'RED'
    if any(x in t for x in ['주의', '오류', '점검', '취약', '결함', '경고', '비상']): return 'AMBER'
    return 'GREEN'

# --- [4] 강력한 크롤링 로직 ---
def crawl():
    print("🕷️ 네이버 뉴스 크롤링 시작 (차단 우회 시도)...")
    results = []
    
    for kw in KEYWORDS:
        try:
            # 뉴스 검색 URL (최신순 정렬)
            url = f"https://search.naver.com/search.naver?where=news&query={kw}&sort=1"
            res = requests.get(url, headers=get_headers(), timeout=10)
            
            if res.status_code != 200:
                print(f"   ⚠️ [{kw}] 차단됨 (Status: {res.status_code})")
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.select("a.news_tit")
            
            if not items:
                print(f"   ⚠️ [{kw}] 검색 결과 없음 (HTML 구조 변경 가능성)")
                continue

            count = 0
            for item in items[:3]:
                title = item.get_text()
                link = item['href']
                
                # 링크 유효성 체크
                if not link.startswith("http"): continue

                results.append({
                    "keyword": kw,
                    "title": title,
                    "link": link,
                    "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "risk": get_risk(title)
                })
                count += 1
            print(f"   ✅ [{kw}] {count}건 수집 성공")
            time.sleep(random.uniform(0.5, 1.5)) # 인간처럼 보이게 딜레이 추가

        except Exception as e:
            print(f"   ❌ [{kw}] 에러: {e}")
            pass
    
    return results

# --- [5] 실행 및 데이터 처리 ---
data = crawl()

# 데이터가 없으면 비상용 데이터 생성 (화면 멈춤 방지)
if not data:
    print("🚑 모든 크롤링 실패 -> 비상용 데이터 생성")
    data = [{"keyword": "알림", "title": "네이버 접속이 차단되었습니다. 잠시 후 다시 시도하세요.", "link": "#", "date": datetime.datetime.now().strftime("%Y-%m-%d"), "risk": "RED"}]

# ★ 핵심: Base64로 인코딩 (HTML 깨짐 원천 차단)
json_str = json.dumps(data, ensure_ascii=False)
b64_data = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')

print(f"📊 최종 데이터: {len(data)}건 처리 완료.")

# --- [6] HTML 생성 (전문가용 디자인) ---
html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Security Watch</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;500;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Pretendard', sans-serif; background: #f8fafc; }}
        .glass-card {{ background: white; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
        .glass-card:hover {{ transform: translateY(-2px); transition: 0.2s; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-color: #3b82f6; }}
    </style>
</head>
<body class="text-slate-800">

    <nav class="bg-slate-900 text-white h-16 sticky top-0 z-50 px-6 flex items-center justify-between shadow-lg">
        <div class="flex items-center gap-2 font-bold text-lg">
            <i class="ph-fill ph-robot text-blue-400"></i> AI Security Watch
        </div>
        <div class="text-xs bg-slate-800 px-3 py-1 rounded-full text-slate-300 border border-slate-700">
            Last Update: {datetime.datetime.now().strftime("%H:%M:%S")}
        </div>
    </nav>

    <div class="max-w-7xl mx-auto p-6 space-y-6">
        
        <div class="glass-card p-6 bg-gradient-to-r from-slate-800 to-slate-900 text-white border-none">
            <h2 class="font-bold text-lg mb-2 flex items-center gap-2"><i class="ph-duotone ph-brain"></i> 실시간 분석 리포트</h2>
            <p id="ai-msg" class="text-sm text-slate-300 bg-white/10 p-3 rounded-lg backdrop-blur-sm">데이터 분석 중...</p>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="glass-card p-5 border-l-4 border-blue-500">
                <p class="text-xs text-slate-500 font-bold uppercase">수집된 기사</p>
                <h3 id="kpi-total" class="text-3xl font-bold text-slate-800 mt-1">-</h3>
            </div>
            <div class="glass-card p-5 border-l-4 border-red-500 bg-red-50/10">
                <p class="text-xs text-red-600 font-bold uppercase">심각(Critical)</p>
                <h3 id="kpi-red" class="text-3xl font-bold text-red-600 mt-1">-</h3>
            </div>
            <div class="glass-card p-5 border-l-4 border-amber-500">
                <p class="text-xs text-amber-600 font-bold uppercase">주의(Warning)</p>
                <h3 id="kpi-amber" class="text-3xl font-bold text-amber-600 mt-1">-</h3>
            </div>
            <div class="glass-card p-5 border-l-4 border-green-500">
                <p class="text-xs text-green-600 font-bold uppercase">주요 키워드</p>
                <h3 id="kpi-kw" class="text-lg font-bold text-green-700 mt-2 truncate">-</h3>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="space-y-6">
                <div class="glass-card p-5">
                    <h3 class="font-bold text-sm text-slate-700 mb-3">위험도 분포</h3>
                    <div class="h-48 relative"><canvas id="chart"></canvas></div>
                </div>
            </div>

            <div class="lg:col-span-2">
                <div class="flex justify-between items-end mb-3 px-1">
                    <h3 class="font-bold text-lg text-slate-800">뉴스 피드</h3>
                    <span id="cnt" class="text-xs font-bold bg-white border px-2 py-1 rounded text-slate-500 shadow-sm">0건</span>
                </div>
                <div id="list" class="space-y-3"></div>
            </div>
        </div>
        
        <footer class="mt-12 py-8 text-center text-xs text-slate-400 border-t">
            Powered by Python Crawler & GitHub Actions
        </footer>
    </div>

    <script>
        // ★★★ Base64 디코딩 (깨짐 방지) ★★★
        const B64_DATA = "{b64_data}";
        
        function decodeData(str) {{
            try {{
                return JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(str), c => c.codePointAt(0))));
            }} catch (e) {{
                console.error(e); return [];
            }}
        }}

        const rawData = decodeData(B64_DATA);

        window.onload = () => {{
            renderDashboard(rawData);
        }};

        function renderDashboard(data) {{
            // 1. KPI
            document.getElementById('kpi-total').textContent = data.length;
            const red = data.filter(d => d.risk === 'RED').length;
            document.getElementById('kpi-red').textContent = red;
            document.getElementById('kpi-amber').textContent = data.filter(d => d.risk === 'AMBER').length;
            
            // 키워드 통계
            if (data.length > 0) {{
                const counts = {{}};
                data.forEach(d => counts[d.keyword] = (counts[d.keyword] || 0) + 1);
                const top = Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b);
                document.getElementById('kpi-kw').textContent = top;
            }}

            // 2. AI Summary
            const msg = document.getElementById('ai-msg');
            if (red > 0) {{
                msg.innerHTML = `현재 <span class="text-red-400 font-bold">심각(Critical) 이슈가 ${{red}}건</span> 감지되었습니다. 즉시 확인 바랍니다.`;
            }} else {{
                msg.innerHTML = `분석 결과, 현재 특이한 보안 위협 징후는 발견되지 않았습니다. (안전)`;
            }}

            // 3. List
            const list = document.getElementById('list');
            list.innerHTML = '';
            document.getElementById('cnt').textContent = `${{data.length}}건`;

            if (data.length === 0) {{
                list.innerHTML = '<div class="p-8 text-center border-dashed border-2 rounded text-slate-400">데이터 없음</div>';
            }} else {{
                data.forEach(d => {{
                    const el = document.createElement('a');
                    el.href = d.link; el.target = "_blank";
                    el.className = "block glass-card p-5 group no-underline relative hover:border-blue-400 transition-all";
                    
                    let badgeClass = "bg-green-100 text-green-700 border-green-200";
                    if(d.risk === 'RED') badgeClass = "bg-red-100 text-red-700 border-red-200";
                    if(d.risk === 'AMBER') badgeClass = "bg-amber-100 text-amber-700 border-amber-200";

                    el.innerHTML = `
                        <div class="flex justify-between items-start gap-4">
                            <div class="flex-1">
                                <div class="flex gap-2 mb-2 items-center flex-wrap">
                                    <span class="text-[10px] px-2 py-0.5 rounded font-bold uppercase border ${{badgeClass}}">${{d.risk}}</span>
                                    <span class="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded border border-slate-200 font-bold">${{d.keyword}}</span>
                                    <span class="text-xs text-slate-400 font-mono">${{d.date}}</span>
                                </div>
                                <div class="font-bold text-slate-800 text-base leading-snug group-hover:text-blue-600 transition-colors">
                                    ${{d.title}}
                                </div>
                            </div>
                            <i class="ph-bold ph-arrow-square-out text-slate-300 text-lg group-hover:text-blue-500"></i>
                        </div>
                    `;
                    list.appendChild(el);
                }});
            }}

            // 4. Chart
            const counts = {{RED: 0, AMBER: 0, GREEN: 0}};
            data.forEach(d => {{
                if (counts[d.risk] !== undefined) counts[d.risk]++;
                else counts.GREEN++;
            }});

            const ctx = document.getElementById('chart');
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Critical', 'Warning', 'Safe'],
                    datasets: [{{
                        data: [counts.RED, counts.AMBER, counts.GREEN],
                        backgroundColor: ['#ef4444', '#f59e0b', '#22c55e'],
                        borderWidth: 0
                    }}]
                }},
                options: {{ cutout: '75%', plugins: {{ legend: {{ position: 'right', labels: {{ usePointStyle: true, boxWidth: 8 }} }} }} }}
            }});
        }}
    </script>
</body>
</html>
"""

# --- [7] 파일 저장 ---
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print("✨ 업데이트 완료! index.html 파일을 업로드하세요.")

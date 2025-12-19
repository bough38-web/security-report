import requests
from bs4 import BeautifulSoup
import json
import datetime
import base64
import random
import os
import time

# ---------------------------------------------------------
# [1] 설정 및 크롤링 (구글 뉴스 RSS + 네이버 백업)
# ---------------------------------------------------------
KEYWORDS = ["KT텔레캅", "SK쉴더스", "에스원", "보안 사고", "해킹", "개인정보 유출", "산업 재해"]
OUTPUT_FILENAME = "index.html"

def get_risk(title):
    t = title.lower()
    if any(x in t for x in ['사망', '유출', '해킹', '화재', '구속', '긴급', '마비', '충돌', '침해']): return 'RED'
    if any(x in t for x in ['주의', '오류', '점검', '취약', '결함', '경고', '비상', '중단']): return 'AMBER'
    return 'GREEN'

def crawl_google(kw):
    try:
        url = f"https://news.google.com/rss/search?q={kw}&hl=ko&gl=KR&ceid=KR:ko"
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.content, "xml")
        items = soup.find_all("item")
        results = []
        for item in items[:3]:
            dt_str = datetime.datetime.now().strftime("%Y-%m-%d")
            try:
                dt = datetime.datetime.strptime(item.pubDate.text, "%a, %d %b %Y %H:%M:%S %Z")
                dt_str = dt.strftime("%Y-%m-%d")
            except: pass
            
            results.append({
                "keyword": kw, "title": item.title.text, "link": item.link.text, "date": dt_str, "risk": get_risk(item.title.text)
            })
        return results
    except: return []

def get_dummy_data():
    return [{"keyword": k, "title": f"[{k}] 현재 수집된 뉴스가 없습니다 (샘플)", "link": "#", "date": datetime.datetime.now().strftime("%Y-%m-%d"), "risk": "GREEN"} for k in KEYWORDS[:5]]

# ---------------------------------------------------------
# [2] 데이터 수집 및 '안전한' 인코딩 (핵심 기술)
# ---------------------------------------------------------
print("🕷️ 데이터 수집 시작...")
final_data = []

# 1. 구글 뉴스 크롤링
for kw in KEYWORDS:
    data = crawl_google(kw)
    if data:
        final_data.extend(data)
    time.sleep(0.1)

# 2. 데이터 없으면 더미 데이터 사용
if not final_data:
    print("🚑 크롤링 실패 -> 비상용 샘플 데이터 생성")
    final_data = get_dummy_data()

# 3. ★ 핵심: 한글 깨짐 방지를 위해 ASCII로 변환 후 Base64 인코딩 ★
# ensure_ascii=True를 쓰면 한글이 \uXXXX 형태의 영어 코드로 변해서 절대 안 깨짐
json_str = json.dumps(final_data, ensure_ascii=True) 
b64_data = base64.b64encode(json_str.encode('ascii')).decode('ascii')

kw_str = json.dumps(KEYWORDS, ensure_ascii=True)
b64_kw = base64.b64encode(kw_str.encode('ascii')).decode('ascii')

print(f"✅ 총 {len(final_data)}건 데이터 처리 완료. HTML 생성 중...")

# ---------------------------------------------------------
# [3] HTML 템플릿 (멈춤 방지 스크립트 포함)
# ---------------------------------------------------------
html_template = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Insight Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;500;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Pretendard', sans-serif; background-color: #f8fafc; color: #1e293b; }
        .glass-card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; transition: all 0.2s; }
        .glass-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-color: #3b82f6; }
        #loader { position: fixed; inset: 0; background: white; z-index: 999; display: flex; flex-direction: column; justify-content: center; align-items: center; }
    </style>
</head>
<body>

    <div id="loader">
        <div class="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4"></div>
        <p class="text-slate-500 font-bold">시스템 초기화 중...</p>
        <p id="error-msg" class="text-xs text-red-500 mt-2 hidden"></p>
    </div>

    <nav class="bg-slate-900 text-white h-16 sticky top-0 z-50 px-6 flex items-center justify-between shadow-lg">
        <div class="flex items-center gap-2 font-bold text-lg">
            <i class="ph-fill ph-shield-check text-blue-400"></i> Security Insight Pro
        </div>
        <div class="text-xs bg-slate-800 px-3 py-1 rounded-full text-slate-300 border border-slate-700">
            Live System
        </div>
    </nav>

    <div class="max-w-7xl mx-auto p-6 space-y-6">
        
        <div class="glass-card p-6 bg-gradient-to-r from-slate-800 to-slate-900 text-white border-none">
            <h2 class="font-bold text-lg mb-3 flex items-center gap-2">
                <i class="ph-duotone ph-cpu"></i> AI Risk Analysis
            </h2>
            <p id="ai-msg" class="text-sm text-slate-300 bg-white/10 p-4 rounded-xl backdrop-blur-sm border border-white/10 leading-relaxed">
                데이터 분석 중...
            </p>
            <div id="quick-btns" class="mt-4 flex flex-wrap gap-2"></div>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="glass-card p-5 border-l-4 border-blue-500">
                <p class="text-xs text-slate-500 font-bold uppercase">Total News</p>
                <h3 id="kpi-total" class="text-3xl font-bold text-slate-800 mt-2">-</h3>
            </div>
            <div class="glass-card p-5 border-l-4 border-red-500 bg-red-50/20">
                <p class="text-xs text-red-600 font-bold uppercase">Critical</p>
                <h3 id="kpi-red" class="text-3xl font-bold text-red-600 mt-2">-</h3>
            </div>
            <div class="glass-card p-5 border-l-4 border-amber-500">
                <p class="text-xs text-amber-600 font-bold uppercase">Warning</p>
                <h3 id="kpi-amber" class="text-3xl font-bold text-amber-600 mt-2">-</h3>
            </div>
            <div class="glass-card p-5 border-l-4 border-green-500">
                <p class="text-xs text-green-600 font-bold uppercase">Key Issue</p>
                <h3 id="kpi-kw" class="text-lg font-bold text-green-700 mt-3 truncate">-</h3>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="space-y-6">
                <div class="glass-card p-5 sticky top-24">
                    <h3 class="font-bold text-sm text-slate-700 mb-4 pb-2 border-b">Control Panel</h3>
                    <div class="space-y-4">
                        <div>
                            <label class="text-xs font-bold text-slate-500 block mb-1">Keyword Filter</label>
                            <select id="sel-kw" class="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm outline-none focus:border-blue-500 cursor-pointer"><option value="all">전체 보기</option></select>
                        </div>
                        <div>
                            <label class="text-xs font-bold text-slate-500 block mb-1">Search</label>
                            <input id="inp-search" type="text" class="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm outline-none focus:border-blue-500" placeholder="제목 검색...">
                        </div>
                    </div>
                </div>
                <div class="glass-card p-5">
                    <h3 class="font-bold text-sm text-slate-700 mb-4">Risk Share</h3>
                    <div class="h-48 relative"><canvas id="chart"></canvas></div>
                </div>
            </div>

            <div class="lg:col-span-2">
                <div class="flex justify-between items-end mb-4 px-1">
                    <h3 class="font-bold text-lg text-slate-800">News Feed</h3>
                    <span id="cnt" class="text-xs font-bold bg-white border px-2 py-1 rounded text-slate-500 shadow-sm">0 items</span>
                </div>
                <div id="list" class="space-y-3"></div>
            </div>
        </div>
        
        <footer class="mt-12 py-8 text-center text-xs text-slate-400 border-t">
            &copy; 2025 Security Insight Pro. Powered by Google News RSS.
        </footer>
    </div>

    <script>
        // ★★★ Base64 데이터 수신 ★★★
        const B64_DATA = "__DATA_B64__";
        const B64_KW = "__KW_B64__";
        
        let rawData = [], keywords = [], filtered = [], myChart = null;

        window.onload = function() {
            try {
                // 1. 디코딩 (atob는 ASCII만 처리하므로, 한글이 \uXXXX로 된 JSON을 파싱하면 됨)
                rawData = JSON.parse(atob(B64_DATA));
                keywords = JSON.parse(atob(B64_KW));
                filtered = [...rawData];

                // 2. 초기화
                init();
                
                // 3. 로딩 제거
                document.getElementById('loader').style.display = 'none';
            } catch (e) {
                console.error(e);
                document.getElementById('error-msg').textContent = "초기화 오류: " + e.message;
                document.getElementById('error-msg').style.display = 'block';
                // 에러 나도 강제로 로딩 끄기
                setTimeout(() => document.getElementById('loader').style.display = 'none', 1000);
            }
        };

        function init() {
            const btnArea = document.getElementById('quick-btns');
            const sel = document.getElementById('sel-kw');
            
            keywords.forEach(k => {
                const opt = document.createElement('option');
                opt.value = k; opt.textContent = k;
                sel.appendChild(opt);
                
                const btn = document.createElement('button');
                btn.className = "px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-700 text-slate-300 hover:bg-blue-500 hover:text-white transition-colors border border-slate-600";
                btn.textContent = k;
                btn.onclick = () => { sel.value = k; update(); };
                btnArea.appendChild(btn);
            });
            update();
        }

        function update() {
            const kw = document.getElementById('sel-kw').value;
            const search = document.getElementById('inp-search').value.toLowerCase();

            filtered = rawData.filter(d => {
                return (kw === 'all' || d.keyword === kw) && d.title.toLowerCase().includes(search);
            });
            render();
        }

        function render() {
            // KPI
            document.getElementById('kpi-total').textContent = filtered.length;
            const red = filtered.filter(d=>d.risk==='RED').length;
            document.getElementById('kpi-red').textContent = red;
            document.getElementById('kpi-amber').textContent = filtered.filter(d=>d.risk==='AMBER').length;
            
            if(filtered.length > 0) {
                const c = {};
                filtered.forEach(d=>c[d.keyword]=(c[d.keyword]||0)+1);
                const top = Object.keys(c).reduce((a,b)=>c[a]>c[b]?a:b);
                document.getElementById('kpi-kw').textContent = top;
            } else {
                document.getElementById('kpi-kw').textContent = "-";
            }

            // AI Summary
            const msg = document.getElementById('ai-msg');
            if(red > 0) {
                msg.innerHTML = `⚠️ 현재 <span class="text-red-400 font-bold">심각(Critical) 등급 이슈가 ${red}건</span> 감지되었습니다. 주요 키워드를 확인하세요.`;
            } else {
                msg.innerHTML = `✅ 분석 결과, 현재 특이한 보안 위협 징후는 발견되지 않았습니다. (정상)`;
            }

            // List
            const list = document.getElementById('list');
            list.innerHTML = '';
            document.getElementById('cnt').textContent = `${filtered.length} items`;

            if(filtered.length === 0) {
                list.innerHTML = '<div class="p-12 text-center border-2 border-dashed border-slate-200 rounded-xl text-slate-400">데이터가 없습니다.</div>';
            } else {
                filtered.forEach(d => {
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
                                    <span class="text-[10px] px-2 py-0.5 rounded font-bold uppercase border ${badgeClass}">${d.risk}</span>
                                    <span class="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded border border-slate-200 font-bold tracking-wide">${d.keyword}</span>
                                    <span class="text-xs text-slate-400 font-mono flex items-center gap-1"><i class="ph-bold ph-calendar-blank"></i> ${d.date}</span>
                                </div>
                                <h4 class="font-bold text-slate-800 text-base leading-snug group-hover:text-blue-600 transition-colors">
                                    ${d.title}
                                </h4>
                            </div>
                            <div class="bg-slate-50 p-2 rounded-lg group-hover:bg-blue-50 transition-colors">
                                <i class="ph-bold ph-arrow-up-right text-slate-400 group-hover:text-blue-500 text-lg"></i>
                            </div>
                        </div>
                    `;
                    list.appendChild(el);
                });
            }

            // Chart
            if(myChart) myChart.destroy();
            const counts = {RED:0, AMBER:0, GREEN:0};
            filtered.forEach(d => {
                if(counts[d.risk]!==undefined) counts[d.risk]++;
                else counts.GREEN++;
            });

            const ctx = document.getElementById('chart');
            myChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Critical', 'Warning', 'Safe'],
                    datasets: [{
                        data: [counts.RED, counts.AMBER, counts.GREEN],
                        backgroundColor: ['#ef4444', '#f59e0b', '#22c55e'],
                        borderWidth: 0
                    }]
                },
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false, 
                    cutout: '75%', 
                    plugins: { legend: { position: 'right', labels: { usePointStyle: true, boxWidth: 8, font: { family: 'Pretendard' } } } } 
                }
            });
        }

        document.getElementById('sel-kw').addEventListener('change', update);
        document.getElementById('inp-search').addEventListener('input', update);
    </script>
</body>
</html>
"""

# ---------------------------------------------------------
# [4] 데이터 주입 및 파일 저장
# ---------------------------------------------------------
final_html = html_template.replace("__DATA_B64__", b64_data)
final_html = final_html.replace("__KW_B64__", b64_kw)

with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
    f.write(final_html)

print(f"✨ 생성 완료: {OUTPUT_FILENAME}")
print("1. 생성된 index.html 파일을 깃허브에 올리세요.")
print("2. 이제 로딩 화면에서 절대 멈추지 않습니다.")

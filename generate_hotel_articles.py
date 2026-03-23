#!/usr/bin/env python3
"""
飯店文章自動生成腳本
每天自動生成 3 篇飯店開箱文章
"""

import csv
import random
import os
from datetime import datetime

CSV_FILE = "/Users/o/thaiwonder-ai/www-thaiwonder-cc/E342B777-64FD-4A49-9C9F-FEF4BA635863_EN.csv"
OUTPUT_DIR = "/Users/o/thaiwonder-ai/www-thaiwonder-cc"

# 熱門目的地對應的城市
POPULAR_DESTINATIONS = [
    "Tokyo", "Bangkok", "Paris", "London", "New York", "Singapore", 
    "Hong Kong", "Dubai", "Seoul", "Bali", "Phuket", "Krabi",
    "Kuala Lumpur", "Taipei", "Osaka", "Sydney", "Melbourne",
    "Rome", "Barcelona", "Istanbul", "Milan", "Berlin", "Amsterdam"
]

# Agoda Affiliate 連結範本（需要填入 hotel_id）
AGODA_LINK_TEMPLATE = "https://www.agoda.com/partners/partnersearch.aspx?cid={cid}&hid={hotel_id}"
AGODA_CID = "1961406"

# Klook Widget
KLOOK_WIDGET = '''
<!-- Klook Widget -->
<ins class="klk-aff-widget" data-adid="1242486" data-lang="" data-currency="" data-cardH="126" data-padding="92" data-lgH="470" data-edgeValue="655" data-cid="-1" data-tid="-1" data-amount="3" data-prod="dynamic_widget"><a href="//www.klook.com/">Klook.com</a></ins>
<script type="text/javascript">
(function (d, sc, u) {
 var s = d.createElement(sc),
 p = d.getElementsByTagName(sc)[0];
 s.type = "text/javascript";
 s.async = true;
 s.src = u;
 p.parentNode.insertBefore(s, p);
 })(
 document,
 "script",
 "https://affiliate.klook.com/widget/fetch-iframe-init.js"
 );
</script>
'''

def load_hotels():
    """載入飯店資料"""
    hotels = []
    with open(CSV_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                if row.get('rating_average') and float(row.get('rating_average', 0)) >= 8.0:
                    hotels.append(row)
            except:
                pass
    return hotels

def filter_hotels_by_destination(hotels, destination):
    """過濾特定目的地的飯店"""
    return [h for h in hotels if destination.lower() in h.get('city', '').lower() or 
            destination.lower() in h.get('country', '').lower()]

def generate_article(hotel, date_str):
    """生成飯店開箱文章"""
    hotel_name = hotel.get('hotel_name', 'Unknown Hotel')
    city = hotel.get('city', 'Unknown City')
    country = hotel.get('country', 'Unknown Country')
    address = hotel.get('addressline1', '')
    star = hotel.get('star_rating', '0')
    rating = hotel.get('rating_average', '0')
    reviews = hotel.get('number_of_reviews', '0')
    overview = hotel.get('overview', '')[:500]
    photo1 = hotel.get('photo1', '')
    photo2 = hotel.get('photo2', '')
    photo3 = hotel.get('photo3', '')
    
    # 飯店類型
    acc_type = hotel.get('accommodation_type', 'Hotel')
    
    # 檔名
    safe_name = hotel_name.lower().replace(' ', '-').replace('/', '-')[:50]
    filename = f"hotel-{safe_name}-{date_str}.html"
    
    # 國家名稱翻譯
    country_cn = {
        'Thailand': '泰國', 'Japan': '日本', 'South Korea': '韓國',
        'Indonesia': '印尼', 'Malaysia': '馬來西亞', 'Singapore': '新加坡',
        'Vietnam': '越南', 'Philippines': '菲律宾', 'Cambodia': '柬埔寨',
        'Myanmar': '缅甸', 'France': '法國', 'Italy': '義大利',
        'Spain': '西班牙', 'Germany': '德國', 'Netherlands': '荷蘭',
        'United Kingdom': '英國', 'United States': '美國', 'Australia': '澳洲',
        'New Zealand': '紐西蘭', 'Turkey': '土耳其', 'Israel': '以色列'
    }.get(country, country)
    
    article_title = f"{hotel_name} 住宿推薦：{city} {acc_type}開箱評測"
    
    # 生成文章內容
    content = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article_title} - 旅遊筆記</title>
    <meta name="description" content="探索 {hotel_name} 的完整住宿評測。{city} {country_cn} {acc_type}，評分 {rating} 分，{reviews}則評論。立即預訂享受優惠價格！">
    <meta name="keywords" content="{hotel_name}, {city} 住宿, {city} 飯店, {country_cn} 旅遊, {acc_type} 推薦">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{article_title}">
    <meta property="og:description" content="{city} {country_cn} {acc_type}，評分 {rating} 分，{reviews}則評論">
    <meta property="og:image" content="{photo1}">
    <meta property="og:type" content="article">
    
    <!-- JSON-LD Structured Data -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Hotel",
        "name": "{hotel_name}",
        "address": "{{"@type": "PostalAddress", "addressLocality": "{city}", "addressCountry": "{country}"}}",
        "starRating": {{"@type": "Rating", "ratingValue": "{star}"}},
        "aggregateRating": {{"@type": "AggregateRating", "ratingValue": "{rating}", "reviewCount": "{reviews}"}},
        "photo": "{photo1}"
    }}
    </script>
    
    <link rel="stylesheet" href="styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&family=Noto+Serif+TC:wght@400;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <nav class="logo-nav">
        <a href="index.html" class="logo">
            <img src="logo-light.svg" alt="旅遊筆記" class="logo-light">
            <img src="logo-dark.svg" alt="旅遊筆記" class="logo-dark">
        </a>
    </nav>

    <header class="article-header" style="background-image: url('{photo1}?w=1920&q=80')">
        <div class="article-header-overlay"></div>
        <div class="article-header-content">
            <div class="container">
                <div class="article-meta">
                    <span class="tag">{country_cn}</span>
                    <span>{datetime.now().strftime('%Y年%m月')}</span>
                </div>
                <h1 class="article-title">{hotel_name}</h1>
                <p class="article-subtitle">{city} {country_cn} {acc_type}住宿開箱</p>
            </div>
        </div>
    </header>

    <section class="article-body">
        <div class="container">
            <div class="article-rating">
                <span class="stars">{"⭐" * int(float(star))}</span>
                <span class="rating">{rating} / 10</span>
                <span class="reviews">({reviews} 則評論)</span>
            </div>
            
            <h2>關於 {hotel_name}</h2>
            <p>{overview}</p>
            
            <h2>飯店設施與服務</h2>
            <ul>
                <li>📍 地址：{address}</li>
                <li>🏨 星级：{"⭐" * int(float(star))} ({star} 星)</li>
                <li>🛏️ 房型：{acc_type}</li>
                <li>📝 評分：{rating} 分（{reviews}則評論）</li>
                <li>🚪 入住時間：{hotel.get('checkin', 'N/A')}</li>
                <li>🚪 退房時間：{hotel.get('checkout', 'N/A')}</li>
            </ul>
            
            <h2>客房介紹</h2>
            <div class="photo-gallery">
                <img src="{photo1}?w=800&q=80" alt="{hotel_name} 客房 1">
                <img src="{photo2}?w=800&q=80" alt="{hotel_name} 客房 2">
                <img src="{photo3}?w=800&q=80" alt="{hotel_name} 客房 3">
            </div>
            
            <h2>為什麼選擇 {hotel_name}？</h2>
            <ul>
                <li>✅ 評分高：{rating} 分，獲得廣泛好评</li>
                <li>✅ 位置便利：位於{city}市中心</li>
                <li>✅ 設施完善：提供Wi-Fi、停車場等基本設施</li>
                <li>✅ 評論眾多：{reviews}則真實住客評價</li>
            </ul>
            
            <h2>預訂資訊</h2>
            <p>想要入住{hotel_name}嗎？透過以下連結預訂可獲得優惠價格：</p>
            <a href="https://www.agoda.com/partners/partnersearch.aspx?cid={AGODA_CID}&hid={hotel.get('hotel_id')}" target="_blank" class="booking-btn">🏨 查看最低房價</a>
            
            <div class="travel-tips">
                <h3>📌 旅遊小提示</h3>
                <ul>
                    <li>建議提前預訂，特別是旺季時段</li>
                    <li>比較不同訂房網站的價格</li>
                    <li>查看最新評論以了解最新狀況</li>
                    <li>注意取消政策的彈性</li>
                    <li>如有問題可直接聯繫飯店</li>
                </ul>
            </div>
            
            {KLOOK_WIDGET}
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <p>旅遊筆記 • 用文字記錄旅途</p>
        </div>
    </footer>
</body>
</html>'''
    
    return filename, content

def main():
    print("📚 載入飯店資料...")
    all_hotels = load_hotels()
    print(f"   找到 {len(all_hotels)} 間高評分飯店")
    
    # 隨機選擇 3 個目的地
    destinations = random.sample(POPULAR_DESTINATIONS, 3)
    date_str = datetime.now().strftime('%Y%m%d')
    
    print(f"\n✍️  生成 {len(destinations)} 篇飯店文章...")
    
    for dest in destinations:
        hotels = filter_hotels_by_destination(all_hotels, dest)
        if not hotels:
            print(f"   ⚠️ 找不到 {dest} 的飯店，跳過")
            continue
            
        # 選擇評分最高的飯店
        hotel = max(hotels, key=lambda x: float(x.get('rating_average', 0)))
        
        filename, content = generate_article(hotel, date_str)
        
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ 已生成：{filename}")
    
    print(f"\n✨ 完成！")

if __name__ == "__main__":
    main()

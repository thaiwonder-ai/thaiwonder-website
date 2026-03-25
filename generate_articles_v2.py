#!/usr/bin/env python3
"""
飯店文章自動生成腳本 v2
每天自動生成 3 篇飯店開箱 + 3 篇旅遊景點文章
"""

import csv
import random
import os
import urllib.request
import uuid
from datetime import datetime

CSV_FILE = "/Users/o/thaiwonder-ai/www-thaiwonder-cc/E342B777-64FD-4A49-9C9F-FEF4BA635863_EN.csv"
OUTPUT_DIR = "/Users/o/thaiwonder-ai/www-thaiwonder-cc"
CACHE_DIR = "/Users/o/thaiwonder-ai/www-thaiwonder-cc/hotel_images"

AGODA_CID = "1961406"

# 旅遊目的地配置（使用 Unsplash 免費圖庫）
DESTINATIONS = [
    {"city": "Tokyo", "country": "Japan", "country_cn": "日本", "keyword": "tokyo city night", "intro": "東京，這座充滿活力的都市，結合了傳統與現代的完美平衡。"},
    {"city": "Paris", "country": "France", "country_cn": "法國", "keyword": "paris eiffel tower", "intro": "巴黎，永遠的浪漫之都，每個轉角都有說不完的故事。"},
    {"city": "Bangkok", "country": "Thailand", "country_cn": "泰國", "keyword": "bangkok temple sunset", "intro": "曼谷，一座兼具古老寺廟與現代購物的多元都市。"},
    {"city": "Seoul", "country": "South Korea", "country_cn": "韓國", "keyword": "seoul street korean", "intro": "首爾，K-POP 與傳統韓屋交織的獨特城市。"},
    {"city": "Bali", "country": "Indonesia", "country_cn": "印尼", "keyword": "bali beach temple", "intro": "峇里島，遠離塵囂的天堂，每一口呼吸都是享受。"},
    {"city": "Singapore", "country": "Singapore", "country_cn": "新加坡", "keyword": "singapore marina bay", "intro": "新加坡，花園城市的極致展現，乾淨又充滿驚喜。"},
    {"city": "Sydney", "country": "Australia", "country_cn": "澳洲", "keyword": "sydney opera house", "intro": "雪梨，港灣城市的美麗代表，陽光與海灘的代名詞。"},
    {"city": "London", "country": "United Kingdom", "country_cn": "英國", "keyword": "london big ben", "intro": "倫敦，古典與創意並存的國際大都會。"},
    {"city": "New York", "country": "United States", "country_cn": "美國", "keyword": "new york times square", "intro": "紐約，永遠不會無聊的城市，機會與夢想的競技場。"},
    {"city": "Dubai", "country": "United Arab Emirates", "country_cn": "杜拜", "keyword": "dubai skyline burj khalifa", "intro": "杜拜，奢華的極致展現，未來城市的最佳範例。"},
]

# 隨機風格句子（讓文章更像人寫的）
INTRO_STYLES = [
    "說實話，這次入住經驗讓我蠻驚喜的。",
    "這次住的飯店，整體來說給了我不小的驚喜。",
    "住了好幾天，必須說這間飯店有它的獨到之處。",
    "說真的，一分錢一分貨，但這間飯店有些地方超出期待。",
    "經過多方比較後，我最終選了這間，住了幾天的心得是...",
]

HIGHLIGHT_STYLES = [
    "最讓我印象深刻的是...",
    "如果要說最滿意的部分，應該是...",
    "說到這間飯店的亮點，我覺得是...",
    "實際住下來，我最喜歡的是...",
    "如果要推薦，我會說一定要體驗...",
]

TIPS_STYLES = [
    "給未來想住這裡的朋友幾個小建議：",
    "住過後的真心小提醒：",
    "以過來人的經驗，有幾點想提醒大家：",
    "如果要我給點建議，我會說：",
]

# 內建飯店資料（CSV 不存在時的後備方案）
FALLBACK_HOTELS = [
    {"hotel_name": "Park Hyatt Tokyo", "city": "Tokyo", "country": "Japan", "addressline1": "3-7-1-2 Nishi Shinjuku", "star_rating": "5", "rating_average": "9.2", "number_of_reviews": "2850", "overview": "位於東京繁華的新宿區，享有東京全景的豪華飯店。"},
    {"hotel_name": "Shangri-La Hotel Paris", "city": "Paris", "country": "France", "addressline1": "16 Avenue d'Iéna", "star_rating": "5", "rating_average": "9.4", "number_of_reviews": "3200", "overview": "巴黎市中心精品飯店，鄰近香榭麗舍大道。"},
    {"hotel_name": "The St. Regis Bangkok", "city": "Bangkok", "country": "Thailand", "addressline1": "159 Rajadamri Road", "star_rating": "5", "rating_average": "9.1", "number_of_reviews": "2100", "overview": "曼谷五星級飯店，提供極致奢華體驗。"},
    {"hotel_name": "Four Seasons Hotel Seoul", "city": "Seoul", "country": "South Korea", "addressline1": "97 Bongeunsa-ro", "star_rating": "5", "rating_average": "9.3", "number_of_reviews": "1950", "overview": "首爾江南區五星級飯店，結合韓國傳統與現代設計。"},
    {"hotel_name": "COMO Uma Ubud", "city": "Bali", "country": "Indonesia", "addressline1": "Jalan Raya Sanggingan", "star_rating": "5", "rating_average": "9.5", "number_of_reviews": "890", "overview": "峇里島烏布精品度假村，置身叢林與梯田間。"},
    {"hotel_name": "Marina Bay Sands", "city": "Singapore", "country": "Singapore", "addressline1": "10 Bayfront Avenue", "star_rating": "5", "rating_average": "8.9", "number_of_reviews": "8500", "overview": "新加坡地標飯店，三座塔樓與天空泳池聞名世界。"},
    {"hotel_name": "Park Hyatt Sydney", "city": "Sydney", "country": "Australia", "addressline1": "7 Hickson Road", "star_rating": "5", "rating_average": "9.2", "number_of_reviews": "1650", "overview": "悉尼港畔五星級飯店，緊鄰歌劇院。"},
    {"hotel_name": "The Savoy London", "city": "London", "country": "United Kingdom", "addressline1": "Strand, London", "star_rating": "5", "rating_average": "9.1", "number_of_reviews": "4200", "overview": "倫敦經典五星級飯店，百年歷史奢華象徵。"},
    {"hotel_name": "The Plaza New York", "city": "New York", "country": "United States", "addressline1": "Fifth Avenue at Central Park South", "star_rating": "5", "rating_average": "9.0", "number_of_reviews": "3800", "overview": "紐約經典飯店，中央公園旁的地標建築。"},
    {"hotel_name": "Burj Al Arab", "city": "Dubai", "country": "United Arab Emirates", "addressline1": "Jumeirah Beach Road", "star_rating": "5", "rating_average": "9.6", "number_of_reviews": "5600", "overview": "杜拜七星級飯店，世界最奢華飯店之一。"},
]

def load_hotels():
    """載入飯店資料"""
    hotels = []
    
    # 嘗試從 CSV 載入
    if os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        if row.get('rating_average') and float(row.get('rating_average', 0)) >= 8.0:
                            hotels.append(row)
                    except:
                        pass
            if hotels:
                print(f"✅ 從 CSV 載入 {len(hotels)} 間飯店")
                return hotels
        except Exception as e:
            print(f"⚠️ CSV 讀取失敗: {e}")
    
    # 使用內建後備資料
    print(f"✅ 使用內建飯店資料 ({len(FALLBACK_HOTELS)} 間)")
    return FALLBACK_HOTELS

def filter_hotels_by_city(hotels, city):
    return [h for h in hotels if city.lower() in h.get('city', '').lower()]

def resize_image_url(url, width=600):
    """調整圖片尺寸（使用 Unsplash URL 參數）"""
    if not url:
        return ""
    # 對於 Unsplash 圖片，可以調整尺寸
    if 'unsplash.com' in url:
        return url.split('?')[0] + f"?w={width}&q=80&auto=format"
    return url

def generate_hotel_article(hotel, dest_info):
    """生成飯店開箱文章"""
    hotel_name = hotel.get('hotel_name', 'Unknown Hotel')
    city = hotel.get('city', 'Unknown City')
    country = hotel.get('country', 'Unknown Country')
    address = hotel.get('addressline1', '未提供')
    star = int(float(hotel.get('star_rating', 0)))
    rating = float(hotel.get('rating_average', 0))
    reviews = int(float(hotel.get('number_of_reviews', 0)))
    overview = hotel.get('overview', '')[:600]
    photos = [hotel.get(f'photo{i}', '') for i in range(1, 6)]
    photos = [p for p in photos if p][:5]  # 取最多5張
    
    acc_type = hotel.get('accommodation_type', 'Hotel')
    
    # 國家翻譯
    country_cn = {
        'Thailand': '泰國', 'Japan': '日本', 'South Korea': '韓國',
        'Indonesia': '印尼', 'Malaysia': '馬來西亞', 'Singapore': '新加坡',
        'Vietnam': '越南', 'Philippines': '菲律宾', 'France': '法國',
        'Italy': '義大利', 'Spain': '西班牙', 'Germany': '德國',
        'Netherlands': '荷蘭', 'United Kingdom': '英國', 'United States': '美國',
        'Australia': '澳洲', 'Turkey': '土耳其', 'UAE': '杜拜'
    }.get(country, country)
    
    date_str = datetime.now().strftime('%Y%m%d')
    safe_name = hotel_name.lower().replace(' ', '-').replace('/', '-')[:40]
    filename = f"hotel-{safe_name}-{date_str}.html"
    
    intro = random.choice(INTRO_STYLES)
    highlight = random.choice(HIGHLIGHT_STYLES)
    tips = random.choice(TIPS_STYLES)
    
    header_photo = photos[0] if photos else "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=1920"
    content = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{hotel_name} 住宿心得 - 旅遊筆記</title>
    <meta name="description" content="{intro} {city} {country_cn} {acc_type}住宿開箱，評分 {rating} 分。">
    <meta name="keywords" content="{hotel_name}, {city} 住宿, 飯店開箱, {country_cn} 旅遊">
    <meta property="og:title" content="{hotel_name} 住宿心得">
    <meta property="og:description" content="{city} {acc_type}，評分 {rating} 分">
    <meta property="og:image" content="{photos[0] if photos else ''}">
    <meta property="og:type" content="article">
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Hotel",
        "name": "{hotel_name}",
        "address": {{"@type": "PostalAddress", "addressLocality": "{city}", "addressCountry": "{country}"}},
        "starRating": {{"@type": "Rating", "ratingValue": "{star}"}},
        "aggregateRating": {{"@type": "AggregateRating", "ratingValue": "{rating}", "reviewCount": "{reviews}"}}
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

    <header class="article-header" style="background-image: url('{header_photo}?w=1920&q=80')">
        <div class="article-header-overlay"></div>
        <div class="article-header-content">
            <div class="container">
                <div class="article-meta">
                    <span class="tag">{country_cn}</span>
                    <span>{datetime.now().strftime('%Y年%m月')}</span>
                </div>
                <h1 class="article-title">{hotel_name}</h1>
                <p class="article-subtitle">{city} {acc_type} 住宿開箱</p>
            </div>
        </div>
    </header>

    <section class="article-body">
        <div class="container">
            <div class="article-rating">
                <span class="stars">{"⭐" * star}</span>
                <span class="rating">{rating} / 10</span>
                <span class="reviews">({reviews} 則評論)</span>
            </div>
            
            <h2>前言</h2>
            <p>{intro}這次去{city}，在眾多住宿選擇中，我選了{hotel_name}。住了幾天下來，有些心得想跟大家分享。</p>
            
            <h2>關於飯店</h2>
            <p>{overview}</p>
            
            <h2>房間設施</h2>
            <ul>
                <li>📍 地址：{address}</li>
                <li>🏨 星级：{"⭐" * star}（{star}星）</li>
                <li>🛏️ 類型：{acc_type}</li>
                <li>📝 評分：{rating} 分（{reviews}則評論）</li>
                <li>🚪 入住：{hotel.get('checkin', 'N/A')} / 退房：{hotel.get('checkout', 'N/A')}</li>
            </ul>
            
            <h2>實拍照片</h2>
            <div class="photo-gallery">'''
    
    for i, photo in enumerate(photos[:4]):  # 最多4張
        if photo:
            content += f'''
                <img src="{resize_image_url(photo, 600)}" alt="{hotel_name} 實拍{i+1}">'''
    
    content += f'''
            </div>
            
            <h2>住宿體驗</h2>
            <p>{highlight}整體的住宿體驗來說，我覺得這間飯店的位置相當便利，周邊生活機能也不錯。房間的話，以這個價位來說算是合理，該有的設施都有。</p>
            <p>如果要我給這次住宿打分數，我會給{rating}分。扣分的地方主要是一些細節處理，例如服務速度還可以再快一點，但整體來說是滿意的體驗。</p>
            
            <h2>預訂資訊</h2>
            <p>有興趣的朋友可以透過以下連結查看最新房價：</p>
            <a href="https://www.agoda.com/partners/partnersearch.aspx?cid={AGODA_CID}&hid={hotel.get('hotel_id')}" target="_blank" class="booking-btn">🏨 查看房價</a>
            
            <div class="travel-tips">
                <h3>📌 住後心得小提醒</h3>
                <ul>
                    <li>建議提前預訂，旺季很容易滿房</li>
                    <li>可以寫信給飯店溝通特殊需求</li>
                    <li>機場接送服務可以事先預訂</li>
                    <li>週邊機能不錯，可以逛逛當地市集</li>
                    <li>退房時間前可以寄放行李</li>
                </ul>
            </div>
            
            <ins class="klk-aff-widget" data-adid="1242486" data-lang="" data-currency="" data-cardH="126" data-padding="92" data-lgH="470" data-edgeValue="655" data-cid="-1" data-tid="-1" data-amount="3" data-prod="dynamic_widget"><a href="//www.klook.com/">Klook.com</a></ins>
            <script type="text/javascript">
            (function (d, sc, u) {{var s = d.createElement(sc), p = d.getElementsByTagName(sc)[0]; s.type = "text/javascript"; s.async = true; s.src = u; p.parentNode.insertBefore(s, p); }})(document, "script", "https://affiliate.klook.com/widget/fetch-iframe-init.js");
            </script>
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

def generate_destination_article(dest):
    """生成旅遊景點文章"""
    city = dest["city"]
    country = dest["country"]
    country_cn = dest["country_cn"]
    keyword = dest["keyword"]
    intro = dest["intro"]
    
    date_str = datetime.now().strftime('%Y%m%d')
    safe_name = city.lower().replace(' ', '-')
    filename = f"travel-{safe_name}-{date_str}.html"
    
    content = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{city} 旅遊指南 - {country_cn} 自由行攻略 | 旅遊筆記</title>
    <meta name="description" content="{intro}探索{city}必去景點、美食推薦、交通攻略。這篇帶你深入了解{country_cn}最迷人的城市！">
    <meta name="keywords" content="{city} 旅遊, {country_cn} 自由行, {city} 景點, {city} 美食, {city} 攻略">
    <meta property="og:title" content="{city} 旅遊指南 - {country_cn} 自由行攻略">
    <meta property="og:description" content="{intro}必去景點、美食推薦、交通攻略">
    <meta property="og:image" content="https://images.unsplash.com/photo-1506905925346-21bda4d32dfb?w=1200&q=80">
    <meta property="og:type" content="article">
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "TravelGuide",
        "name": "{city} 旅遊指南",
        "description": "{intro}探索{city}必去景點",
        "address": {{"@type": "PostalAddress", "addressLocality": "{city}", "addressCountry": "{country}"}}
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

    <header class="article-header" style="background-image: url('https://images.unsplash.com/photo-1506905925346-21bda4d32dfb?w=1920&q=80')">
        <div class="article-header-overlay"></div>
        <div class="article-header-content">
            <div class="container">
                <div class="article-meta">
                    <span class="tag">{country_cn}</span>
                    <span>{datetime.now().strftime('%Y年%m月')}</span>
                </div>
                <h1 class="article-title">{city}</h1>
                <p class="article-subtitle">{country_cn} 旅遊完全指南</p>
            </div>
        </div>
    </header>

    <section class="article-body">
        <div class="container">
            <h2>關於 {city}</h2>
            <p>{intro}這次去{city}，真的讓我愛上這座城市。從繁華的市區到充滿歷史氣息的老街，每個角落都有驚喜。</p>
            
            <h2>推薦景點</h2>
            <p>如果你是第一次去{city}，這幾個地方千萬不要錯過：</p>
            <ul>
                <li>🏛️ 市中心廣場 - 感受城市的心跳</li>
                <li>🌆 夜景觀景台 - 夕陽和夜景都超美</li>
                <li>🎨 藝術特區 - 很多獨立小店和咖啡廳</li>
                <li>🛍️ 購物區 - 從精品到平價都有</li>
                <li>🍜 美食街 - 當地小吃聚集地</li>
            </ul>
            
            <h2>美食推薦</h2>
            <p>說到{city}的美食，幾家我個人很喜歡的：</p>
            <ul>
                <li>🍜 巷子裡的拉麵店 - 當地人推薦的老店</li>
                <li>☕ 網紅咖啡廳 - 拍照打卡聖地</li>
                <li>🦐 海鮮餐廳 - 新鮮又便宜</li>
            </ul>
            
            <h2>交通建議</h2>
            <p>{city}的交通算是便利，地鐵可以到達大部分景點。如果時間允許，我推薦用走的，很多風景是坐車會錯過的。</p>
            
            <h2>最佳旅遊時間</h2>
            <p>一般來說，春秋季是天氣最舒適的時候。夏天雖然熱，但活動比較多；冬天則是淡季，機票住宿都比較便宜。</p>
            
            <div class="travel-tips">
                <h3>📌 旅遊小提醒</h3>
                <ul>
                    <li>建議購買當地交通卡，省錢又方便</li>
                    <li>有些景點需要提前預約門票</li>
                    <li>兌換貨幣時多比較幾家</li>
                    <li>隨身帶雨具，天氣說變就變</li>
                    <li>保持開放心態，迷路也是旅行的一部分</li>
                </ul>
            </div>
            
            <ins class="klk-aff-widget" data-adid="1242486" data-lang="" data-currency="" data-cardH="126" data-padding="92" data-lgH="470" data-edgeValue="655" data-cid="-1" data-tid="-1" data-amount="3" data-prod="dynamic_widget"><a href="//www.klook.com/">Klook.com</a></ins>
            <script type="text/javascript">
            (function (d, sc, u) {{var s = d.createElement(sc), p = d.getElementsByTagName(sc)[0]; s.type = "text/javascript"; s.async = true; s.src = u; p.parentNode.insertBefore(s, p); }})(document, "script", "https://affiliate.klook.com/widget/fetch-iframe-init.js");
            </script>
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
    
    # 選擇 3 個目的地
    dests = random.sample(DESTINATIONS, 3)
    cities = [d["city"] for d in dests]
    date_str = datetime.now().strftime('%Y%m%d')
    
    print(f"\n✍️  生成 3 篇旅遊景點文章...")
    for dest in dests:
        filename, content = generate_destination_article(dest)
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ {filename}")
    
    print(f"\n✍️  生成 3 篇飯店開箱文章...")
    for dest in dests:
        hotels = filter_hotels_by_city(all_hotels, dest["city"])
        if not hotels:
            # 嘗試用國家搜尋
            hotels = [h for h in all_hotels if dest["country"].lower() in h.get('country', '').lower()]
        
        if not hotels:
            print(f"   ⚠️ 找不到 {dest['city']} 的飯店")
            continue
        
        hotel = random.choice(hotels[:50])  # 從評分最高的50間選
        filename, content = generate_hotel_article(hotel, dest)
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ {filename}")
    
    print(f"\n✨ 完成！共生成 6 篇文章")

if __name__ == "__main__":
    main()

# 旅遊網站文章規範

## SEO 基本要求

每篇文章都要有：

### 1. Meta Tags
```html
<meta name="description" content="...">
<meta name="keywords" content="...">
```

### 2. Open Graph
```html
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:image" content="...">
<meta property="og:type" content="article">
```

### 3. JSON-LD Structured Data
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "標題",
  "image": "圖片網址",
  "author": "旅遊筆記",
  "datePublished": "2024-XX-XX"
}
</script>
```

## 內容要求

- 字數：1500-2000 字
- 章節：至少 5 個 h2 標題
- 景點：3-5 個（含經緯度）
- 美食：3 個（含地址）
- 旅遊時間：最佳月份 + 原因
- 小提示：5則

## 圖片

使用 Unsplash 免費圖庫

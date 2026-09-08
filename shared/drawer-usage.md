# 共用左側選單使用說明

## 檔案

- `shared/drawer.css` — 樣式
- `shared/drawer.js` — 開關邏輯 + 深色模式

## 引入方式（推薦）

在 `<head>` 加入：

```html
<link rel="stylesheet" href="shared/drawer.css">
```

在 `</body>` 前加入：

```html
<script src="shared/drawer.js"></script>
```

## 必要 HTML 結構（放在 `<body>` 最前面）

```html
<!-- 浮動按鈕 -->
<button type="button" class="menu-fab" id="menu-fab" aria-label="開啟選單" onclick="openDrawer()">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
    <path d="M4 7h16M4 12h16M4 17h16"/>
  </svg>
</button>

<!-- 遮罩 -->
<div class="drawer-overlay" id="drawer-overlay" onclick="closeDrawer()"></div>

<!-- 側邊選單 -->
<aside class="drawer" id="drawer" role="dialog" aria-label="選單">
  <div class="drawer-header">
    <span class="drawer-title">選單</span>
    <button type="button" class="drawer-close" aria-label="關閉" onclick="closeDrawer()">×</button>
  </div>
  <nav class="drawer-nav">
    <!-- 依工具自行修改連結 -->
    <a href="index.html">數值計算器</a>
    <a href="item.html">道具例表</a>
    <!-- 之後可再加其他工具 -->
  </nav>
  <div class="drawer-footer">
    <button type="button" id="theme-toggle" class="theme-in-drawer" aria-label="切換深色模式" title="切換深色模式">
      <span class="theme-toggle-icon">🌙</span>
      <span class="theme-toggle-text">深色模式</span>
    </button>
  </div>
</aside>
```

## 注意事項

1. 頁面需已定義 CSS 變數 `--card`、`--text`、`--muted`、`--border`、`--accent`（或使用 fallback）。
2. 深色模式依賴 `body.dark-theme` class。
3. 目前 localStorage key 為 `pokemon-calc-theme`，之後若要跨工具共用可改成統一 key。
4. 目前頁面會自動依檔名加上 `.active`。

## 之後擴充

把其他工具（QR、抽蛋…）的連結加進 `.drawer-nav` 即可。

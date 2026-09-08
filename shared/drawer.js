/**
 * 共用左側選單 (drawer) + 深色模式切換
 * 使用方式：
 * 1. 引入 drawer.css
 * 2. 在 <body> 開頭貼上選單 HTML 結構
 * 3. 引入本檔 drawer.js
 * 4. （可選）用 data-menu-items 或直接改 HTML 裡的連結
 */

(function () {
  'use strict';

  function openDrawer() {
    document.getElementById('drawer')?.classList.add('open');
    document.getElementById('drawer-overlay')?.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    document.getElementById('drawer')?.classList.remove('open');
    document.getElementById('drawer-overlay')?.classList.remove('open');
    document.body.style.overflow = '';
  }

  // 暴露到全域，讓 onclick 也能呼叫
  window.openDrawer = openDrawer;
  window.closeDrawer = closeDrawer;

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeDrawer();
  });

  // ===== 深色模式 =====
  var themeToggle = document.getElementById('theme-toggle');
  var THEME_KEY = 'pokemon-calc-theme'; // 之後可改成共用 key，例如 'fangyin-theme'

  function applyTheme(theme) {
    var dark = theme === 'dark';
    document.body.classList.toggle('dark-theme', dark);
    if (themeToggle) {
      var icon = themeToggle.querySelector('.theme-toggle-icon');
      var text = themeToggle.querySelector('.theme-toggle-text');
      if (icon) icon.textContent = dark ? '☀️' : '🌙';
      if (text) text.textContent = dark ? '淺色模式' : '深色模式';
      themeToggle.setAttribute('aria-label', dark ? '切換淺色模式' : '切換深色模式');
      themeToggle.title = dark ? '切換淺色模式' : '切換深色模式';
    }
  }

  // 初始化
  var saved = localStorage.getItem(THEME_KEY);
  applyTheme(saved === 'dark' ? 'dark' : 'light');

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      var next = document.body.classList.contains('dark-theme') ? 'light' : 'dark';
      applyTheme(next);
      localStorage.setItem(THEME_KEY, next);
    });
  }

  // 標記目前頁面 active（依檔名）
  var path = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  document.querySelectorAll('.drawer-nav a').forEach(function (a) {
    var href = (a.getAttribute('href') || '').toLowerCase();
    if (href === path || (path === '' && href === 'index.html')) {
      a.classList.add('active');
    }
  });
})();

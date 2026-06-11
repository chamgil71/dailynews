/**
 * nav.js — 공유 네비게이션 모듈
 * - id="site-nav": .hnav-tab 구조로 완전 교체 (archive 등 legacy 헤더)
 * - .header-nav: 활성 탭 border 색상만 보정 (header.html include 페이지)
 */
(function () {
  'use strict';
  var path = decodeURIComponent(location.pathname);

  // GitHub Pages base path 제거
  var stripped = path.replace(/^\/dailynews/, '') || '/';
  var parts = stripped.split('/').filter(Boolean);
  // 마지막 요소가 .html 파일이면 depth에서 제외
  var depth = parts.length;
  if (depth > 0 && parts[depth - 1].indexOf('.') !== -1) depth -= 1;
  var prefix = depth > 0 ? new Array(depth + 1).join('../') : '';

  var section  = parts[0] || '';
  var fileName = parts[parts.length - 1] || '';
  var active =
    section === 'stock'    ? 'stock'    :
    section === 'ai-issue' ? 'ai-issue' :
    section === 'news'     ? 'news'     :
    fileName === 'archive.html' ? 'archive' : '';

  var tabs = [
    { key: 'news',     href: 'index.html',   label: '뉴스 브리핑' },
    { key: 'ai-issue', href: 'ai-issue/',    label: 'AI이슈' },
    { key: 'stock',    href: 'stock/',       label: '주식 시황' },
    { key: 'archive',  href: 'archive.html', label: '아카이브' },
  ];

  // 탭별 활성 border 색상 (뉴스=파랑, AI이슈=보라, 주식=초록)
  var tabColors = {
    'news':     'var(--color-blue-light)',
    'ai-issue': '#a78bfa',
    'stock':    'var(--color-up)',
    'archive':  'var(--color-blue-light)',
  };

  // ── id="site-nav" 대상 (archive 등 legacy 헤더) ─────────────────
  var navEl = document.getElementById('site-nav');
  if (navEl) {
    navEl.className = 'header-nav';
    navEl.removeAttribute('id');
    navEl.innerHTML = tabs.map(function (t) {
      var isActive = t.key === active;
      var cls = 'hnav-tab' + (isActive ? ' active' : '');
      var style = isActive ? ' style="border-bottom-color:' + tabColors[t.key] + '"' : '';
      return '<a class="' + cls + '"' + style
           + ' href="' + prefix + t.href + '"'
           + ' data-section="' + t.key + '">'
           + '<span class="tab-label">' + t.label + '</span></a>';
    }).join('\n');
  }

  // ── .header-nav 대상 (header.html include 페이지) ────────────────
  // Jinja2가 이미 active 클래스를 설정했으므로 border 색상만 보정
  var headerNav = document.querySelector('header .header-nav');
  if (headerNav) {
    var activeTabs = headerNav.querySelectorAll('.hnav-tab.active');
    for (var i = 0; i < activeTabs.length; i++) {
      var sec = activeTabs[i].getAttribute('data-section');
      if (sec && tabColors[sec]) {
        activeTabs[i].style.borderBottomColor = tabColors[sec];
      }
    }
  }
})();

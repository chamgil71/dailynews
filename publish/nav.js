/**
 * nav.js — 공유 네비게이션 모듈
 * id="site-nav" 요소에 탭 HTML을 주입.
 * Vercel(/) 및 GitHub Pages(/dailynews/) 양쪽 지원.
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

  var section = parts[0] || '';
  var fileName = parts[parts.length - 1] || '';
  var active =
    section === 'stock'    ? 'stock'    :
    section === 'ai-issue' ? 'ai-issue' :
    section === 'news'     ? 'news'     :
    fileName === 'archive.html' ? 'archive'  : '';

  var tabs = [
    { key: 'news',     href: 'index.html',   label: '📰 뉴스 브리핑' },
    { key: 'ai-issue', href: 'ai-issue/',    label: '🤖 AI이슈' },
    { key: 'stock',    href: 'stock/',       label: '📊 주식 시황' },
    { key: 'archive',  href: 'archive.html', label: '📚 아카이브' },
  ];

  var navEl = document.getElementById('site-nav');
  if (!navEl) return;

  navEl.innerHTML = tabs.map(function (t) {
    var cls = t.key === active ? ' class="active"' : '';
    return '<a' + cls + ' href="' + prefix + t.href + '">' + t.label + '</a>';
  }).join('\n');
})();

/**
 * nav.js — 공유 네비게이션 모듈
 * - id="site-nav": .hnav-tab 구조로 완전 교체 (legacy 헤더)
 * - .header-nav: 활성 탭 border+background 색상 보정
 */
(function () {
  'use strict';
  var path = decodeURIComponent(location.pathname);
  var stripped = path.replace(/^\/dailynews/, '') || '/';
  var parts = stripped.split('/').filter(Boolean);
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

  // 탭 하나의 정보(경로·라벨·아이콘·활성색)를 한 곳에 모아 관리
  var tabs = [
    { key: 'news', href: 'index.html', label: '뉴스 브리핑',
      border: '#60a5fa', bg: 'rgba(96,165,250,.12)',
      icon: '<svg viewBox="0 0 16 16" width="15" height="15" fill="currentColor" style="flex-shrink:0"><path d="M0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2zm15 2h-4v3h4V4zm0 4h-4v3h4V8zm0 4h-4v2h3a1 1 0 0 0 1-1v-1zm-5 2v-2H6v2h4zm-5 0v-2H1v1a1 1 0 0 0 1 1h3zm-4-4h4V8H1v4zm0-5h4V4H1v3zm5-3v3h4V4H6zm4 4H6v3h4V8z"/></svg>' },
    { key: 'ai-issue', href: 'ai-issue/', label: 'AI이슈',
      border: '#a78bfa', bg: 'rgba(167,139,250,.12)',
      icon: '<svg viewBox="0 0 16 16" width="15" height="15" fill="currentColor" style="flex-shrink:0"><path d="M5 0a.5.5 0 0 1 .5.5V2h1V.5a.5.5 0 0 1 1 0V2h1V.5a.5.5 0 0 1 1 0V2h1V.5a.5.5 0 0 1 1 0V2A2.5 2.5 0 0 1 14 4.5h1.5a.5.5 0 0 1 0 1H14v1h1.5a.5.5 0 0 1 0 1H14v1h1.5a.5.5 0 0 1 0 1H14A2.5 2.5 0 0 1 11.5 12V14H11v1.5a.5.5 0 0 1-1 0V14H9v1.5a.5.5 0 0 1-1 0V14H7v1.5a.5.5 0 0 1-1 0V14H5.5A2.5 2.5 0 0 1 3 11.5H1.5a.5.5 0 0 1 0-1H3v-1H1.5a.5.5 0 0 1 0-1H3v-1H1.5a.5.5 0 0 1 0-1H3A2.5 2.5 0 0 1 5.5 4V2H5V.5A.5.5 0 0 1 5 0zm-.5 4.5v7A1.5 1.5 0 0 0 6 13h4a1.5 1.5 0 0 0 1.5-1.5v-7A1.5 1.5 0 0 0 10 3H6A1.5 1.5 0 0 0 4.5 4.5zM6 5h4a.5.5 0 0 1 0 1H6a.5.5 0 0 1 0-1zm0 2h4a.5.5 0 0 1 0 1H6a.5.5 0 0 1 0-1zm0 2h4a.5.5 0 0 1 0 1H6a.5.5 0 0 1 0-1z"/></svg>' },
    { key: 'stock', href: 'stock/', label: '주식 시황',
      border: '#4ade80', bg: 'rgba(74,222,128,.12)',
      icon: '<svg viewBox="0 0 16 16" width="15" height="15" fill="currentColor" style="flex-shrink:0"><path fill-rule="evenodd" d="M0 0h1v15h15v1H0V0zm10 3.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 .5.5v4a.5.5 0 0 1-1 0V4.9l-3.613 4.417a.5.5 0 0 1-.74.037L7.06 6.767l-3.656 5.027a.5.5 0 0 1-.808-.588l4-5.5a.5.5 0 0 1 .758-.06l2.609 2.61L13.445 4H10.5a.5.5 0 0 1-.5-.5z"/></svg>' },
    { key: 'archive', href: 'archive.html', label: '아카이브',
      border: '#60a5fa', bg: 'rgba(96,165,250,.12)',
      icon: '<svg viewBox="0 0 16 16" width="15" height="15" fill="currentColor" style="flex-shrink:0"><path d="M0 2a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1v7.5a2.5 2.5 0 0 1-2.5 2.5h-9A2.5 2.5 0 0 1 1 12.5V5a1 1 0 0 1-1-1V2zm2 3v7.5A1.5 1.5 0 0 0 3.5 14h9a1.5 1.5 0 0 0 1.5-1.5V5H2zm13-3H1v2h14V2zM5 7.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5z"/></svg>' },
  ];
  var tabByKey = {};
  tabs.forEach(function (t) { tabByKey[t.key] = t; });

  // ── id="site-nav" 대상 (legacy 헤더) ────────────────────────────
  var navEl = document.getElementById('site-nav');
  if (navEl) {
    navEl.className = 'header-nav';
    navEl.removeAttribute('id');
    navEl.innerHTML = tabs.map(function (t) {
      var isActive = t.key === active;
      var cls = 'hnav-tab' + (isActive ? ' active' : '');
      var style = isActive ? ' style="border-bottom-color:' + t.border + ';background:' + t.bg + '"' : '';
      return '<a class="' + cls + '"' + style
           + ' href="' + prefix + t.href + '"'
           + ' data-section="' + t.key + '">'
           + (t.icon || '')
           + '<span class="tab-label"> ' + t.label + '</span></a>';
    }).join('\n');
  }

  // ── .header-nav 대상 (header.html include / editorial 페이지) ────
  var headerNav = document.querySelector('header .header-nav');
  if (headerNav) {
    var activeTabs = headerNav.querySelectorAll('.hnav-tab.active');
    for (var i = 0; i < activeTabs.length; i++) {
      var sec = activeTabs[i].getAttribute('data-section');
      var t = tabByKey[sec];
      if (t) {
        activeTabs[i].style.borderBottomColor = t.border;
        activeTabs[i].style.background = t.bg;
      }
    }
  }
})();

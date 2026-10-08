/* 시안 C 영문 보기(2026-10-08) — KOR/ENG 를 누르면 같은 페이지에서 글만 바꾼다(시안 단계 방식; 정식 공개 때는 언어별 주소로).
   사전은 i18n-en.js(국문영문글정리.xlsx 에서 생성 — content-export/tools/i18n_js.py). 페이지에 표식을 달지 않고
   화면 글을 사전에서 찾아 바꾼다 :
     1) 안에 블록이 없는 원소(제목 · 문단 · 링크 …)는 통째 글(<br> 은 줄바꿈)로 찾고, 맞으면 영문으로 갈아 끼운다
     2) 아니면 그 안의 글 조각(텍스트 노드)을 하나씩 찾는다
     3) alt · aria-label · placeholder · title 도 같은 사전으로
   고른 언어는 이 브라우저에 기억한다(localStorage 'apro-lang'). KOR 로 돌아가면 다시 불러 원문으로.
   스크립트가 나중에 채우는 글(게시판 쪽 넘김 · 상세 글 · 팝업)은 MutationObserver 가 따라가 바꾼다.
   바꾸지 않을 자리는 data-no-i18n */
(function(){
  var KEY = 'apro-lang';
  function get(){ try { return localStorage.getItem(KEY) || 'ko'; } catch(e){ return 'ko'; } }
  function set(v){ try { localStorage.setItem(KEY, v); } catch(e){} }
  var lang = get(), root = document.documentElement;
  var HAN = /[가-힣]/;
  var SKIP = { SCRIPT:1, STYLE:1, NOSCRIPT:1, TEXTAREA:1, svg:1, SVG:1, CODE:1 };
  var INLINE = { A:1, B:1, I:1, EM:1, STRONG:1, SPAN:1, SMALL:1, BR:1, SUP:1, SUB:1, MARK:1, U:1, LABEL:1, TIME:1 };
  var ATTR = ['alt', 'aria-label', 'placeholder', 'title'];
  var BR = '\u0001';   /* 글을 모을 때 <br> 자리 표시 */
  var D = null, busy = false;

  /* 줄마다 공백 하나 · 줄 사이 \n (사전 열쇠와 같은 꼴). 소스의 줄바꿈은 공백이고 <br> 자리만 줄바꿈이다 */
  function flat(s){
    return s.replace(/[ \t\r\n\f\v ]+/g, ' ').split(BR)
            .map(function(l){ return l.trim(); }).filter(Boolean).join('\n');
  }
  function textOf(el){
    /* white-space:pre-line 자리(홈 히어로 문구)는 소스 줄바꿈이 곧 화면 줄바꿈이다 */
    if(/^pre/.test(getComputedStyle(el).whiteSpace) && !el.firstElementChild){
      return el.textContent.split('\n').map(function(l){ return l.replace(/\s+/g, ' ').trim(); }).filter(Boolean).join('\n');
    }
    var out = '';
    (function walk(n){
      for(var c = n.firstChild; c; c = c.nextSibling){
        if(c.nodeType === 3) out += c.nodeValue;
        else if(c.nodeType === 1){
          if(c.tagName === 'BR') out += BR;
          else if(!SKIP[c.tagName]) walk(c);
        }
      }
    })(el);
    return flat(out);
  }
  function inlineOnly(el){
    for(var c = el.firstElementChild; c; c = c.nextElementSibling){
      if(!INLINE[c.tagName] || !inlineOnly(c)) return false;
    }
    return true;
  }
  /* 숫자가 바뀌는 글(주식정보 — 스크립트가 매일 채운다)은 사전 대신 꼴로 */
  var PAT = [
    [/^([\d.]+) 종가 기준$/, function(m){ return 'Closing price as of ' + m[1]; }],
    [/^([\d,]+)주$/, function(m){ return m[1] + ' shares'; }],
    [/^([\d,.]+)억원$/, function(m){   /* 1억 = 0.1B */
      var n = parseFloat(m[1].replace(/,/g, '')) / 10;
      return 'KRW ' + n.toLocaleString('en-US', { maximumFractionDigits:1 }) + 'B'; }],
    [/^최고 ([\d,]+) · 최저 ([\d,]+)$/, function(m){ return 'High ' + m[1] + ' · Low ' + m[2]; }]
  ];
  function look(s){
    if(!s || !HAN.test(s)) return null;
    var hit = D[s] || D[s.replace(/\n/g, ' ')];
    if(hit) return hit;
    for(var i = 0; i < PAT.length; i++){ var m = s.match(PAT[i][0]); if(m) return PAT[i][1](m); }
    return null;
  }
  /* 글을 감싸기만 하는 원소(.b > .bt 처럼 자식 하나에 글이 다 든 것)는 그 안쪽에 넣어 꾸밈을 지킨다 */
  function inner(el){
    for(;;){
      var only = null, n = 0, text = false;
      for(var c = el.firstChild; c; c = c.nextSibling){
        if(c.nodeType === 3 && c.nodeValue.trim()) text = true;
        /* 글 없는 꾸밈(점 · 아이콘 span)은 세지 않는다 — 그대로 두고 글 든 쪽에 넣는다 */
        else if(c.nodeType === 1 && c.tagName !== 'svg' && c.tagName !== 'IMG' && c.textContent.trim()){ only = c; n++; }
      }
      if(text || n !== 1 || only.tagName === 'BR') return el;
      el = only;
    }
  }
  function put(el, en){
    /* 글 없는 꾸밈(아이콘 svg · img, 점 span)은 남기고 글만 바꾼다 — 글 앞에 있던 것은 앞에, 뒤에 있던 것은 뒤에 */
    var pre = [], post = [], seen = false;
    [].forEach.call(el.childNodes, function(c){
      var deco = c.nodeType === 1 && c.tagName !== 'BR' && (c.tagName === 'svg' || c.tagName === 'IMG' || !c.textContent.trim());
      if(deco) (seen ? post : pre).push(c);
      else if(c.textContent.trim()) seen = true;
    });
    el.textContent = '';
    pre.forEach(function(k){ el.appendChild(k); });
    en.split('\n').forEach(function(l, i){
      if(i) el.appendChild(document.createElement('br'));
      el.appendChild(document.createTextNode(l));
    });
    post.forEach(function(k){ el.appendChild(k); });
  }
  function doText(t){
    var raw = t.nodeValue, en = look(flat(raw));
    /* 글 안에 줄바꿈이 있으면(white-space:pre-line 으로 줄을 끊는 자리 — 홈 히어로 문구) 영문 줄바꿈도 살린다 */
    if(en) t.nodeValue = raw.match(/^\s*/)[0] + (/\S\n\S/.test(raw.trim()) ? en : en.replace(/\n/g, ' ')) + raw.match(/\s*$/)[0];
  }
  function doAttrs(el){
    ATTR.forEach(function(a){
      var v = el.getAttribute(a), en = v && look(flat(v));
      if(en) el.setAttribute(a, en);
    });
  }
  function tr(node){
    if(node.nodeType === 3){ if(!node.parentElement || !node.parentElement.closest('[data-no-i18n]')) doText(node); return; }
    if(node.nodeType !== 1 || SKIP[node.tagName] || node.closest('[data-no-i18n]')) return;
    doAttrs(node);
    if(!node.firstElementChild || inlineOnly(node)){
      var en = look(textOf(node));
      if(en){ put(inner(node), en); return; }
    }
    for(var c = node.firstChild; c; c = c.nextSibling) tr(c);
  }
  function run(){
    busy = true;
    tr(document.body);
    /* 게시판 건수 '총 <b>n</b>건' — 끝의 '건'은 낱말 하나로 사전에 둘 수 없어 여기서 */
    [].forEach.call(document.querySelectorAll('.clist-hd .count'), function(p){
      [].forEach.call(p.childNodes, function(n){ if(n.nodeType === 3 && n.nodeValue.trim() === '건') n.nodeValue = ' items'; });
    });
    var t = look(flat(document.title)); if(t) document.title = t;
    busy = false;
  }
  function mark(){
    [].forEach.call(document.querySelectorAll('.sf-drop a'), function(a){
      var on = (a.textContent.trim() === 'ENG') === (lang === 'en');
      if(on) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
    });
    [].forEach.call(document.querySelectorAll('.ov-lang'), function(a){ a.textContent = lang === 'en' ? 'KOR' : 'ENG'; });
  }
  function load(cb){
    if(window.APRO_I18N_EN){ D = window.APRO_I18N_EN; return cb(); }
    var s = document.createElement('script');
    s.src = 'i18n-en.js';
    s.onload = function(){ D = window.APRO_I18N_EN || {}; cb(); };
    document.head.appendChild(s);
  }
  /* 국문 이름에 곁들인 영문 꾸밈 줄 — 영문 보기에선 큰 이름과 겹말이 되어 숨긴다(2026-10-08, 방법 1).
     자리: 사업영역 허브 카드 이름 밑(.p-title .en) · 세부 페이지 히어로는 큰 영문 이름(.en)을 두고 작은 국문 자리(.ko)를 숨김 · 다른 사업영역 이동 꼬리표(.bhtag/.bhnow .en)
     · 사업장소재 이름 위(.lc-head .en) · 회사 소개 핵심가치 원 풀이(company-c.html 안 규칙). 새 자리는 data-en-hide 로 */
  var HIDE = 'html[lang="en"] .p-title > .en, html[lang="en"] .sf-hero h1 > .ko, html[lang="en"] .bhtag > .en, html[lang="en"] .bhnow > .en,'
           + 'html[lang="en"] .lc-head > .en, html[lang="en"] [data-en-hide]{display:none !important}';
  function english(){
    root.lang = 'en';
    var st = document.createElement('style'); st.textContent = HIDE; document.head.appendChild(st);
    load(function(){
      run();
      new MutationObserver(function(ms){
        if(busy) return;
        busy = true;
        ms.forEach(function(m){
          if(m.type === 'characterData') doText(m.target);
          /* 바뀐 원소를 통째로 다시 본다 — 글이 조각(텍스트 노드 여럿)으로 들어와도 원소 글 전체로 찾도록 */
          else if(m.addedNodes.length && m.target.isConnected) tr(m.target);
        });
        busy = false;
      }).observe(document.body, { childList:true, subtree:true, characterData:true });
    });
  }
  /* 언어 고르기 — GNB 드롭다운(KOR · ENG)과 전체 메뉴의 언어 링크 */
  document.addEventListener('click', function(e){
    var a = e.target.closest && e.target.closest('.sf-drop a, .ov-lang');
    if(!a) return;
    e.preventDefault();
    var want = a.classList.contains('ov-lang') ? (lang === 'en' ? 'ko' : 'en') : (a.textContent.trim() === 'ENG' ? 'en' : 'ko');
    if(want === lang) return;
    set(want);
    if(want === 'ko'){ location.reload(); return; }
    lang = 'en'; mark(); english();
  }, true);

  function start(){ mark(); if(lang === 'en') english(); }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();

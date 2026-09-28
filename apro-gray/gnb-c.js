/* ── 시안 C — GNB 메가 판 (A 방식, gnb-c.css 참고) ──────────────────────────
   대분류에 커서가 오면 한 장뿐인 판이 열리고, 커서가 바나 판 위에 있는 동안 열려 있다.
   둘 다 벗어나면 짧게 기다렸다 닫는다 — 바와 판은 따로 떨어진 요소라 그 사이를 지나는
   동안 깜빡이지 않게 하는 여유다. 판은 대분류에서만 연다(로고 · 도구 위에서는 안 연다).

   A-1 의 판 스크립트(business-layout.js 와 각 장 <script>)는 그대로 남아 있다 —
   li[data-mega] 가 가리키던 판(#mega-biz 등)을 C 에서 걷어 냈으므로 그 스크립트는
   판을 찾지 못해 조용히 지나가고, 같은 묶음 안의 언어 선택만 제 일을 한다 */
(function(){
  var gnb = document.querySelector('.sf-gnb');
  var mega = document.getElementById('cMega');
  if(!gnb || !mega) return;
  var menus = gnb.querySelector('.sf-menus');
  if(!menus) return;
  var items = [].slice.call(menus.children);
  var cols = [].slice.call(mega.querySelectorAll('.c-col'));

  /* 밑줄 폭 = 글자 폭 — 링크는 칸 폭(--mm-col)이라 글자만 재서 --lw 로 준다. 글꼴이 늦게 오면 다시 잰다 */
  function measure(){
    items.forEach(function(li){
      var a = li.querySelector('a'); if(!a) return;
      var r = document.createRange(), n = a.firstChild;
      if(!n || n.nodeType !== 3) return;
      r.selectNodeContents(n);
      var w = r.getBoundingClientRect().width;
      if(w) a.style.setProperty('--lw', Math.round(w) + 'px');
    });
  }
  measure();
  window.addEventListener('load', measure);
  window.addEventListener('resize', measure);
  if(document.fonts && document.fonts.ready) document.fonts.ready.then(measure);

  /* 판은 바 바로 밑 층에 둔다 — 바의 층이 장마다 다르다(세부 넷 60 · 나머지 100) */
  var z = parseInt(getComputedStyle(gnb).zIndex, 10);
  if(z > 0) mega.style.zIndex = z - 1;

  var t = 0, isOpen = false;
  function mark(i){
    items.forEach(function(li, k){
      var on = k === i;
      li.classList.toggle('is-open', on);
      var a = li.querySelector('a');
      if(a) a.setAttribute('aria-expanded', isOpen && on ? 'true' : 'false');
    });
  }
  function open(i){
    clearTimeout(t);
    if(!isOpen){
      isOpen = true;
      gnb.classList.add('c-open');
      mega.classList.add('open');
      mega.setAttribute('aria-hidden', 'false');
    }
    if(typeof i === 'number') mark(i);
  }
  function close(){
    clearTimeout(t);
    if(!isOpen) return;
    isOpen = false;
    gnb.classList.remove('c-open');
    mega.classList.remove('open');
    mega.setAttribute('aria-hidden', 'true');
    mark(-1);
  }
  function hold(){ clearTimeout(t); }
  function leave(){ clearTimeout(t); t = setTimeout(close, 140); }

  items.forEach(function(li, i){
    li.addEventListener('mouseenter', function(){ open(i); });
    li.addEventListener('focusin', function(){ open(i); });
  });
  cols.forEach(function(c, i){
    c.addEventListener('mouseenter', function(){ if(isOpen) mark(i); });
    c.addEventListener('focusin', function(){ open(i); });
  });
  /* 바 위(로고 · 도구 포함)에 머무는 동안은 열린 판을 붙들기만 한다 */
  gnb.addEventListener('mouseenter', hold);
  gnb.addEventListener('mouseleave', leave);
  mega.addEventListener('mouseenter', hold);
  mega.addEventListener('mouseleave', leave);

  /* 탭으로 바와 판 밖으로 나가면 닫는다 */
  document.addEventListener('focusin', function(e){
    if(!isOpen) return;
    if(menus.contains(e.target) || mega.contains(e.target)) return;
    close();
  });
  document.addEventListener('keydown', function(e){ if(e.key === 'Escape') close(); });
  /* 전체 메뉴를 열면 판은 비켜 준다 */
  var burger = gnb.querySelector('.menu-toggle');
  if(burger) burger.addEventListener('click', close);
  /* 바가 접히면(세부 장의 탭 바 고정 · .nav-hide) 판도 닫는다 */
  window.addEventListener('scroll', function(){
    if(isOpen && gnb.classList.contains('nav-hide')) close();
  }, { passive: true });
})();

/* ── 시안 C — 바 바탕이 뒤를 따라 바뀐다 (A 방식, gnb-c.css 참고) ─────────────
   얼굴은 셋이다 — 히어로 위(.c-clear) · 어두운 바탕 위(.c-dark) · 밝은 바탕 위(기본).
   히어로는 첫 화면의 큰 그림(홈 .v2banner · 세부 .sf-hero · 회사정보 .ci-top)이다. 그 밑변이
   바 밑변 아래에 있는 동안은 투명하다(A 의 홈 · 콘텐츠 장과 같은 판정).
   히어로를 벗어나면 바 뒤를 몇 군데 찍어 본다. A 는 장마다 "이 장은 흰색 · 푸터는 검정"을
   손으로 적어 두었지만 C 는 스물세 장의 짜임이 제각각이라, 실제로 바 뒤에 무엇이 칠해져
   있는지를 읽는다 — 찍은 자리에서 위로 올라가며 처음 만나는 사진(img · video · 배경 그림)은
   어두운 것으로, 불투명한 바탕색은 밝기로 가른다. 다섯 자리 중 셋 이상이 어두우면 어둡다 */
(function(){
  var gnb = document.querySelector('.sf-gnb');
  if(!gnb) return;
  var hero = document.querySelector('.v2banner, .sf-hero, .ci-top');
  var skip = ['.sf-gnb', '.c-mega', '.navover', '.totop'];
  function skipped(el){
    for(var i = 0; i < skip.length; i++){ if(el.closest && el.closest(skip[i])) return true; }
    return false;
  }
  function rgba(s){
    var m = s && s.match(/rgba?\(([^)]+)\)/);
    if(!m) return null;
    var p = m[1].split(',').map(parseFloat);
    return { r:p[0], g:p[1], b:p[2], a:p.length > 3 ? p[3] : 1 };
  }
  /* 한 점의 바탕이 어두운가 — true / false */
  function darkAt(x, y){
    var list = document.elementsFromPoint(x, y), el = null;
    for(var i = 0; i < list.length; i++){ if(!skipped(list[i])){ el = list[i]; break; } }
    for(; el && el.nodeType === 1; el = el.parentElement){
      var tag = el.tagName;
      if(tag === 'IMG' || tag === 'VIDEO' || tag === 'CANVAS') return true;
      var cs = getComputedStyle(el);
      if(/url\(/.test(cs.backgroundImage)) return true;
      var c = rgba(cs.backgroundColor);
      if(c && c.a >= .5) return (0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b) / 255 < .5;
    }
    return false;                                  /* 끝까지 투명 → 흰 body */
  }
  var face = null;
  function apply(){
    var h = gnb.offsetHeight, next;
    if(hero && hero.getBoundingClientRect().bottom > h && hero.getBoundingClientRect().top <= 0){
      next = 'c-clear';
    } else {
      var w = document.documentElement.clientWidth, y = Math.max(1, Math.round(h / 2)), n = 0;
      [.1, .3, .5, .7, .9].forEach(function(f){ if(darkAt(Math.round(w * f), y)) n++; });
      next = n >= 3 ? 'c-dark' : '';
    }
    if(next === face) return;
    gnb.classList.remove('c-clear', 'c-dark');
    if(next) gnb.classList.add(next);
    face = next;
  }
  var ticking = false;
  function req(){ if(!ticking){ ticking = true; requestAnimationFrame(function(){ ticking = false; apply(); }); } }
  window.addEventListener('scroll', req, { passive: true });
  window.addEventListener('resize', req);
  window.addEventListener('load', apply);
  apply();
})();

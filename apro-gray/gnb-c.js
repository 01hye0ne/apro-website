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

/* ── 시안 C — 바 바탕 (gnb-c.css 참고) ─────────────────────────────────────
   얼굴은 둘이다 — 히어로 위 완전 투명(.c-clear) · 그 밖 흰 반투명(기본).
   히어로는 첫 화면의 큰 그림(홈 .v2banner · 세부 .sf-hero · 회사정보 .ci-top)이다. 그 밑변이
   바 밑변 아래에 있는 동안은 투명하다. 히어로가 없는 장은 늘 흰 반투명이다.
   (2026-09-28 까지는 히어로를 벗어난 뒤 바 뒤를 다섯 점 찍어 어두우면 어두운 유리로 바꿨다 — 걷었다) */
(function(){
  var gnb = document.querySelector('.sf-gnb');
  if(!gnb) return;
  var hero = document.querySelector('.v2banner, .sf-hero, .ci-top');
  /* 히어로가 바 밑에 조금만 남아 있을 때(밑변이 바 안쪽) — 사업영역 세부는 한 장씩 넘어가며 인트로가
     바 바로 아래에 멈춰, 바 뒤에 히어로 사진 밑단이 깔린 채로 남는다. 흰 반투명이 그 사진을 비쳐
     회색빛이 돌았다(2026-09-28). 그 틈에는 반투명 대신 불투명 흰색(.c-solid)을 깐다 — 흰 바탕 위의
     흰 반투명과 눈으로는 같은 흰색이라 얼굴은 여전히 둘이다 */
  var face = null;
  function apply(){
    var h = gnb.offsetHeight, r = hero && hero.getBoundingClientRect();
    var next = !r ? '' : (r.bottom > h && r.top <= 0) ? 'c-clear' : (r.bottom > 0 ? 'c-solid' : '');
    if(next === face) return;
    gnb.classList.remove('c-clear', 'c-solid');
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

/* 사업영역 세부 — 붙박인 줄에 .is-stuck 을 단다(margin-c.css 가 밑줄 · 그림자 · 흰 단색을 준다).
   모바일(767 이하)은 아코디언 제목 줄(.sf-acc-hd), 태블릿(768~1180)은 가로 인덱스 띠(.sf-railwrap).
   GNB 밑(--c-gnb-h)에 닿아 있고 제 장 윗선은 이미 그 위로 올라간 때만 붙은 것이다 */
(function(){
  var hds = [].slice.call(document.querySelectorAll('.sf-secs>.sf-sec>.sf-acc-hd, .sf-railwrap'));
  if(!hds.length) return;
  var raf = 0;
  function apply(){
    raf = 0;
    var g = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--c-gnb-h')) || 0;
    var any = false;
    hds.forEach(function(h){
      /* 장 끝에서 밀려 올라가는 동안에도 바 밑에 걸쳐 있으면 붙은 것으로 친다 */
      var on = getComputedStyle(h).position === 'sticky' &&
               h.parentNode.getBoundingClientRect().top < g - 1 &&
               h.getBoundingClientRect().bottom > g + 1;
      h.classList.toggle('is-stuck', on);
      if(on) any = true;
    });
    /* 붙은 줄이 있으면 문서에도 표시 — GNB 가 유리를 걷고 흰 단색이 된다(margin-c.css) */
    document.documentElement.classList.toggle('c-acc-stuck', any);
  }
  function req(){ if(!raf) raf = requestAnimationFrame(apply); }
  window.addEventListener('scroll', req, { passive: true });
  window.addEventListener('resize', req);
  document.addEventListener('click', function(e){ if(e.target.closest && e.target.closest('.sf-acc-btn')) req(); });
  apply();
})();

/* 맨 위로 가기(#totop) — 화면 절반을 내려가면 뜨고, 누르면 맨 위로. 홈 · 회사소개는 제 장 안에 같은 스크립트가 있어
   data-wired 로 한 번만 잇는다(콘텐츠 열세 장은 이것뿐이다) */
(function(){
  var btn = document.getElementById('totop');
  if(!btn || btn.dataset.wired) return;
  btn.dataset.wired = '1';
  function on(){ btn.classList.toggle('is-visible', window.scrollY > window.innerHeight * .5); }
  window.addEventListener('scroll', on, { passive: true });
  on();
  btn.addEventListener('click', function(){ window.scrollTo({ top: 0, behavior: 'smooth' }); });
})();

/* 콘텐츠 장 본문 블록 등장(gnb-c.css "콘텐츠 장 움직임") — 화면에 들어온 낱낱에 .c-in 을 단다. 한 번만 */
(function(){
  var body = document.querySelector('.cs-split .cs-body');
  if(!body || !('IntersectionObserver' in window)) return;
  if(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var items = [].slice.call(body.querySelectorAll('.cblock>*:not(.cgrid):not(.ccreed):not(.cnews)'));
  [].forEach.call(body.querySelectorAll('.cgrid,.ccreed,.cnews'), function(g){
    [].forEach.call(g.children, function(li, i){ li.style.setProperty('--ci', Math.min(i, 8)); items.push(li); });
  });
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('c-in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px' });
  items.forEach(function(el){ io.observe(el); });
  document.documentElement.classList.add('c-rv');
})();

/* 사업영역 세부 태블릿(768~1180) — 그림을 붙박이 기둥(.sf-figstack)에 둔다(margin-c.css).
   business-layout.js 는 1180 이하에서 그림을 장 안으로 옮기는데(A · A-1 과 함께 쓰는 파일이라 그대로 둔다),
   시안 C 는 태블릿도 넓은 화면처럼 기둥에서 그림을 민다 — 그 뒤에 돌아 768 이상이면 기둥으로 되돌리고,
   폰(767 이하)이면 장 안에 둔다. 옮긴 뒤에는 장 스크립트에 알려(c-figs-moved) 그림 자리를 다시 잡게 한다 */
(function(){
  var stack = document.querySelector('.sf-figstack');
  var secs = [].slice.call(document.querySelectorAll('.sf-secs .sf-sec'));
  if(!stack || !secs.length) return;
  var pairs = [];
  secs.forEach(function(sec){
    var ph = document.querySelector('.sf-ph[data-for="' + sec.id + '"]');
    if(ph) pairs.push({ sec: sec, ph: ph });
  });
  var mq = window.matchMedia('(min-width:901px)');   /* 좁은 태블릿(768~900)은 장 안에 둔다(같은 날 요청) */
  function sync(){
    var moved = false;
    pairs.forEach(function(p){
      if(mq.matches){
        if(p.ph.parentNode !== stack){ stack.appendChild(p.ph); moved = true; }
      }else if(p.ph.parentNode !== p.sec){
        p.sec.insertBefore(p.ph, p.sec.firstChild);
        p.ph.style.transform = ''; p.ph.style.visibility = ''; p.ph.style.removeProperty('--zoom');
        moved = true;
      }
    });
    if(moved) window.dispatchEvent(new Event('c-figs-moved'));
    measure();
  }
  /* 태블릿 — 기둥의 줄 ↔ 그림 사이와 그림 키를 재어 글 쪽이 같은 자리에 앉게 한다(margin-c.css). 화면 키에만 달려 스크롤과 무관 */
  var tab = window.matchMedia('(min-width:901px) and (max-width:1180px)'), root = document.documentElement;
  var fline = document.querySelector('.sf-figcol>.sf-line');
  function measure(){
    if(!tab.matches || !fline){ root.style.removeProperty('--c-fig-gap'); root.style.removeProperty('--c-fig-h'); return; }
    root.style.setProperty('--c-fig-gap', Math.round(stack.getBoundingClientRect().top - fline.getBoundingClientRect().bottom) + 'px');
    root.style.setProperty('--c-fig-h', Math.round(stack.getBoundingClientRect().height) + 'px');
  }
  /* business-layout.js 가 같은 폭 변화에 그림을 먼저 옮긴 뒤에 돈다 */
  function later(){ setTimeout(sync, 0); }
  if(mq.addEventListener) mq.addEventListener('change', later); else if(mq.addListener) mq.addListener(later);
  var big = window.matchMedia('(min-width:1181px)');
  if(big.addEventListener) big.addEventListener('change', later); else if(big.addListener) big.addListener(later);
  window.addEventListener('resize', measure);
  sync();
})();

/* 에너지 인프라 03 솔루션 — 넓은 태블릿(901~1180) 붙박이 윗단의 키를 장마다 재어 --c-ph 로 건다(margin-c.css).
   카드가 그 아래 남은 화면을 채우고, 터치 스냅 자리도 이 값을 쓴다 */
(function(){
  var secs = [].slice.call(document.querySelectorAll('.sf-sec.is-prod'));
  if(!secs.length) return;
  var mq = window.matchMedia('(min-width:901px) and (max-width:1180px)');
  function apply(){
    secs.forEach(function(sec){
      var hd = sec.querySelector('.sf-phead');
      if(mq.matches && hd) sec.style.setProperty('--c-ph', hd.offsetHeight + 'px');
      else sec.style.removeProperty('--c-ph');
    });
  }
  window.addEventListener('resize', apply);
  window.addEventListener('load', apply);
  apply();
})();

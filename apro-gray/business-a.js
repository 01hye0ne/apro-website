/* 사업영역 세부 — A 시안 왼쪽 목록 (2026-09-20 개편)
   섹션(.bsec) 하나에 소분류 카드(.hcard)가 여럿이면, 왼쪽 목록(.bsec-rail)이
   그 카드들의 이름을 차례로 적는다. 목록 글은 카드의 data-tab 을 그대로 읽으므로
   HTML 에 따로 적어 둘 필요가 없다 — 카드를 더하거나 빼면 목록도 따라온다.

   ── 2026-09-20 : 탭 → 스크롤 안내 ───────────────────────────────────
   종전에는 목록이 탭이라, 한 번에 한 카드만 보이고 나머지는 hidden 이었다.
   이제 카드는 전부 펼쳐져 세로로 쌓이고, 목록은 "지금 어디를 읽고 있는지"를
   비추면서 누르면 그 카드로 굴러가는 길잡이가 된다. 그래서
     · 마크업에서 hidden 을 걷었다 (스크립트가 없어도 전부 읽힌다)
     · 누르면 그 카드 윗변이 고정 탭 바 밑으로 오도록 굴린다
     · 스크롤에 따라 aria-current 를 옮긴다
   캐러셀(business-layout.js)은 .hsec 만 보므로 이 페이지들과 겹치지 않는다 */
(function () {
  /* 고정 탭 바(128) + 그 밑 가로선까지(12) + 숨(28). 카드 윗변이 이 선 아래
     로 오도록 굴린다. CSS 의 scroll-margin-top 과 같은 값이다 */
  var OFFSET = 168;
  var reduce = window.matchMedia('(prefers-reduced-motion:reduce)').matches;
  var groups = [];

  /* 태블릿(901~1280)에서는 왼쪽 목록을 걷고, 고정 탭 바가 그 몫을 맡는다
     (2026-09-22 요청) — 사업명 자리에 지금 읽는 소분류 이름이, 소분류 탭 자리에
     그 소분류의 카드 목록이 선다. 두 벌을 따로 만들어 두고 CSS 가 바꿔 낀다 :
     원래 탭(.bnav-ttl · .bnav-tabs)은 손대지 않으므로 business-layout.js 의
     스파이·클릭은 그대로 돈다 */
  var tablet = window.matchMedia('(min-width:901px) and (max-width:1280px)');
  var bwrap = document.querySelector('.bnav-wrap');
  var bnav = bwrap && bwrap.querySelector('.bnav');
  var bsub = null, bidx = null, bbtn = null, bmenu = null;
  if (bnav) {
    /* 소분류 이름은 펼침 단추다 (2026-09-22 UX 점검) — 바가 카드 목록으로 바뀐 뒤에도
       다른 소분류로 바로 건너갈 길을 남긴다. 펼친 목록의 항목은 원래 탭(<a>)을 대신
       눌러 준다 : 굴러가는 자리(아래 capture 핸들러)와 스파이가 한 벌로 남는다.
       이름 뒤 › 는 "소분류 › 그 안의 카드"라는 한 단 아래의 목록임을 알린다 */
    bsub = document.createElement('div'); bsub.className = 'bnav-sub';
    bbtn = document.createElement('button'); bbtn.type = 'button'; bbtn.className = 'bnav-sub-btn';
    bbtn.setAttribute('aria-haspopup', 'true'); bbtn.setAttribute('aria-expanded', 'false');
    var caret = document.createElement('i'); caret.className = 'caret'; caret.setAttribute('aria-hidden', 'true');
    var sep = document.createElement('span'); sep.className = 'sep'; sep.setAttribute('aria-hidden', 'true'); sep.textContent = '›';
    bmenu = document.createElement('ul'); bmenu.className = 'bnav-sub-menu'; bmenu.hidden = true;
    bbtn.appendChild(caret);
    bsub.appendChild(bbtn); bsub.appendChild(sep); bsub.appendChild(bmenu);
    bidx = document.createElement('div'); bidx.className = 'bnav-idx';
    bnav.appendChild(bsub); bnav.appendChild(bidx);

    bnav.querySelectorAll('.bnav-tabs a[href^="#"]').forEach(function (a, i) {
      var li = document.createElement('li');
      var b = document.createElement('button'); b.type = 'button';
      b.setAttribute('data-for', a.getAttribute('href').slice(1));
      var no = document.createElement('span'); no.className = 'no'; no.textContent = ('0' + (i + 1)).slice(-2);
      b.appendChild(no); b.appendChild(document.createTextNode(a.textContent.trim()));
      b.addEventListener('click', function () { openMenu(false); a.click(); });
      li.appendChild(b); bmenu.appendChild(li);
    });
    bbtn.addEventListener('click', function () { openMenu(bmenu.hidden); });
    document.addEventListener('click', function (e) {
      if (!bmenu.hidden && !bsub.contains(e.target)) { openMenu(false); }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !bmenu.hidden) { openMenu(false); bbtn.focus(); }
    });
  }
  function openMenu(on) {
    bmenu.hidden = !on;
    bbtn.setAttribute('aria-expanded', on ? 'true' : 'false');
  }

  /* 목록 칸(.bsec-rail)이 없는 섹션(카드 한 장)도 고정 바에는 제 카드 이름을
     세워야 하므로, 묶음은 카드가 있는 섹션 전부로 만든다 */
  document.querySelectorAll('.bsec').forEach(function (sec) {
    var rail = sec.querySelector('.bsec-rail');
    var cards = [].slice.call(sec.querySelectorAll('.hcard'));
    if (!cards.length) { return; }

    function go(i) {
      var top = window.pageYOffset + cards[i].getBoundingClientRect().top - OFFSET;
      /* 누른 줄을 먼저 켠다 — 부드럽게 굴러가는 동안(0.5초 남짓) 표시가 뒤늦게
         따라오면 누름이 먹지 않은 것처럼 보인다. 굴러가 멈추면 아래 paint 가
         같은 값을 다시 짚으므로 어긋날 일은 없다 */
      mark(i);
      window.scrollTo({ top: Math.max(0, top), behavior: reduce ? 'auto' : 'smooth' });
    }
    function make(parent, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = cards[i].getAttribute('data-tab') || ('0' + (i + 1)).slice(-2);
      b.setAttribute('aria-current', i === 0 ? 'true' : 'false');
      b.addEventListener('click', function () { go(i); });
      parent.appendChild(b);
      return b;
    }

    var btns = [];
    cards.forEach(function (c, i) {
      if (rail) { btns.push(make(rail, i)); }
    });

    /* 고정 바 몫 — 소분류 이름은 탭 띠의 글자를 그대로 읽는다 */
    var name = null, set = null;
    if (bnav) {
      var tab = bnav.querySelector('.bnav-tabs a[href="#' + sec.id + '"]');
      name = document.createElement('span');
      name.textContent = tab ? tab.textContent.trim() : '';
      name.className = 'nm';
      name.hidden = true;
      bbtn.insertBefore(name, bbtn.lastChild);
      set = document.createElement('div');
      set.className = 'bnav-idx-set';
      set.hidden = true;
      bidx.appendChild(set);
      cards.forEach(function (c, i) { btns.push(make(set, i)); });
    }

    var n = cards.length;
    var grp = { sec: sec, cards: cards, at: 0, name: name, set: set };
    function mark(i) {
      if (i === grp.at) { return; }
      grp.at = i;
      for (var j = 0; j < btns.length; j++) {
        btns[j].setAttribute('aria-current', j % n === i ? 'true' : 'false');
      }
    }
    grp.mark = mark;
    groups.push(grp);
  });

  /* 읽고 있는 카드 = 윗변이 기준선(고정 바 밑 + 한 뼘)을 마지막으로 지나간 것.
     아직 아무 카드도 그 선을 넘지 않았으면 첫 카드를 짚는다 — 섹션에 막
     들어섰을 때 목록 첫 줄이 비어 보이지 않게 */
  function paint() {
    var line = OFFSET + 40;
    for (var g = 0; g < groups.length; g++) {
      var grp = groups[g], at = 0;
      for (var i = 0; i < grp.cards.length; i++) {
        if (grp.cards[i].getBoundingClientRect().top <= line) { at = i; }
      }
      grp.mark(at);
    }
    if (!bwrap || !groups.length) { return; }
    /* 고정 바가 비추는 소분류 = 윗변이 같은 기준선을 마지막으로 지나간 섹션.
       ⚠ .bsec 가 아닌 섹션(캐러셀)에 들어서 있으면 원래 탭으로 돌아간다 */
    var cur = null, secs = document.querySelectorAll('.wrap > section[id]');
    for (var s = 0; s < secs.length; s++) {
      if (secs[s].getBoundingClientRect().top <= line) { cur = secs[s]; }
    }
    if (!cur) { cur = groups[0].sec; }
    var on = null;
    for (var k = 0; k < groups.length; k++) {
      var hit = groups[k].sec === cur;
      if (hit) { on = groups[k]; }
      if (groups[k].set && groups[k].set.hidden === hit) {
        groups[k].set.hidden = !hit; groups[k].name.hidden = !hit;
      }
    }
    /* 카드가 한 장뿐인 소분류는 목록이랄 것이 없다 — 칸 하나짜리 판에 제 이름을 한 번 더
       세우는 대신 원래 바(사업명 + 소분류 탭)로 돌아간다 */
    var idx = tablet.matches && !!on && on.cards.length > 1;
    bwrap.classList.toggle('is-idx', idx);
    if (!idx && bmenu && !bmenu.hidden) { openMenu(false); }
    if (bmenu) {
      bmenu.querySelectorAll('button').forEach(function (b) {
        b.setAttribute('aria-current', on && b.getAttribute('data-for') === on.sec.id ? 'true' : 'false');
      });
    }
  }

  /* ── 상단 소분류 탭도 같은 선에 세운다 ──────────────────────────────
     business-layout.js 는 탭을 누르면 섹션 윗변을 화면 맨 위(y=0)로 굴린다 —
     화면을 꽉 채우던 캐러셀 시절의 기준이라, 세로로 쌓이는 A 본문에서는 섹션의
     첫 제목이 고정 바(128+12) 뒤로 숨는다. 그 자리에 왼쪽 목록과 같은 기준을
     쓴다 — 묶음의 첫 줄(.bsec-main 윗변)이 바 밑 168px 에 선다.
     document 의 capture 단계에서 잡아 세운다. 같은 <a> 에 걸린 공용 핸들러가
     먼저 등록돼 있어, 링크 자신에 얹으면 그보다 늦게 불린다 */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('.bnav-tabs a[href^="#"]');
    if (!a) { return; }
    var sec = document.getElementById(a.getAttribute('href').slice(1));
    if (!sec || !sec.classList.contains('bsec')) { return; }
    /* 좁은 화면은 바가 GNB 밑에 붙고 본문도 한 줄로 풀린다 — 공용 규칙대로
       기본 앵커 이동에 맡긴다(.bsec 의 scroll-margin-top 이 자리를 잡는다) */
    if (window.matchMedia('(max-width:900px)').matches) { return; }
    e.preventDefault();
    e.stopPropagation();
    var head = sec.querySelector('.bsec-main') || sec;
    var top = window.pageYOffset + head.getBoundingClientRect().top - OFFSET;
    window.scrollTo({ top: Math.max(0, top), behavior: reduce ? 'auto' : 'smooth' });
  }, true);

  var tick = 0;
  function onScroll() {
    if (tick) { return; }
    tick = requestAnimationFrame(function () { tick = 0; paint(); });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
  window.addEventListener('load', onScroll);
  paint();
})();

/* ── 소분류 머리띠 (2026-09-21) ──────────────────────────────────────
   좁은 화면(≤900)에서는 소분류 탭 띠(.bnav-wrap)를 감추고 소분류 넷이 세로로
   이어진다(A-1 모바일과 같은 짜임). 그러면 "지금 어느 소분류인가"를 알 길이
   탭 띠뿐이었으므로, 각 .bsec 머리에 "01 이차전지 활성화" 띠를 하나 세운다.
   이름은 탭 띠(.bnav-tabs a)의 글자를 그대로 읽는다 — 한 곳만 고치면 된다.
   넓은 화면에서는 CSS 가 감춘다(.bsec-hd) */
(function () {
  var tabs = document.querySelectorAll('.bnav-tabs a[href^="#"]');
  tabs.forEach(function (a, i) {
    var sec = document.querySelector(a.getAttribute('href'));
    if (!sec || !sec.classList.contains('bsec')) { return; }
    var h = document.createElement('h2');
    h.className = 'bsec-hd';
    var no = document.createElement('span'); no.className = 'no'; no.textContent = ('0' + (i + 1)).slice(-2);
    var nm = document.createElement('span'); nm.className = 'nm'; nm.textContent = a.textContent.trim();
    h.appendChild(no); h.appendChild(nm);
    sec.insertBefore(h, sec.firstChild);
  });
})();

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

  document.querySelectorAll('.bsec').forEach(function (sec) {
    var rail = sec.querySelector('.bsec-rail');
    var cards = [].slice.call(sec.querySelectorAll('.hcard'));
    if (!rail || !cards.length) { return; }

    var btns = cards.map(function (card, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = card.getAttribute('data-tab') || ('0' + (i + 1)).slice(-2);
      b.setAttribute('aria-current', i === 0 ? 'true' : 'false');
      rail.appendChild(b);
      b.addEventListener('click', function () {
        var top = window.pageYOffset + cards[i].getBoundingClientRect().top - OFFSET;
        /* 누른 줄을 먼저 켠다 — 부드럽게 굴러가는 동안(0.5초 남짓) 표시가 뒤늦게
           따라오면 누름이 먹지 않은 것처럼 보인다. 굴러가 멈추면 아래 paint 가
           같은 값을 다시 짚으므로 어긋날 일은 없다 */
        mark(i);
        window.scrollTo({ top: Math.max(0, top), behavior: reduce ? 'auto' : 'smooth' });
      });
      return b;
    });

    var grp = { cards: cards, btns: btns, at: 0 };
    function mark(i) {
      if (i === grp.at) { return; }
      grp.at = i;
      for (var j = 0; j < btns.length; j++) {
        btns[j].setAttribute('aria-current', j === i ? 'true' : 'false');
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

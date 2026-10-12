/* 사업영역 세부 장 — 좌측 인덱스(.sf-rail)의 '고무 덩어리' 표시(2026-10-12, 시안 C 시험)
   React Bits 의 Rubber Segment 를 순수 JS 로 옮겼다. 지금 장 표시는 각 링크의 배경을
   켜고 끄는 대신 파란 덩어리 하나가 옮겨 간다. 앞 가장자리가 먼저 뛰고 뒤 가장자리가
   늦게 따라와서, 건너는 동안 늘어났다가 도착하면 살짝 눌리며 선다.
   - 지금 장은 스크롤스파이가 aria-current 로 정한다 — 여기서는 그 변화만 지켜본다
   - 넓은 화면(1181~) : 세로 레일, 덩어리가 링크 칸을 덮는다. 덮인 링크만 흰 글자
   - 태블릿(768~1180) : 가로 탭, 밑줄만 늘어났다 줄어든다. 묶음이 바뀌면 탭 줄이 통째로
     갈리므로 그때는 뛰지 않고 제자리에 놓는다
   - 움직임 줄이기 설정이면 늘 제자리에 놓는다
   세기는 은은하게(motion 취향) — 앞 가장자리만 아주 조금 넘쳤다 돌아온다 */
(function(){
  var rail = document.querySelector('.sf-rail');
  if(!rail) return;
  var links = [].slice.call(rail.querySelectorAll('a'));
  if(!links.length) return;

  var bigMq    = window.matchMedia('(min-width:1181px)');
  var hiddenMq = window.matchMedia('(max-width:767px)');
  var calmMq   = window.matchMedia('(prefers-reduced-motion: reduce)');

  var blob = document.createElement('i');
  blob.className = 'sf-blob';
  blob.setAttribute('aria-hidden', 'true');
  rail.insertBefore(blob, rail.firstChild);
  rail.classList.add('is-rubber');

  /* 가장자리 둘 — a 는 위(왼쪽), b 는 아래(오른쪽). 각자 위치 · 속도 · 목표 */
  var A = { x:0, v:0, t:0 }, B = { x:0, v:0, t:0 };
  var cur = null, raf = 0, last = 0, placed = false, vertical = true;

  /* 앞 가장자리는 단단하고 덜 감쇠(조금 넘친다), 뒤 가장자리는 무르고 거의 임계 감쇠 */
  var LEAD  = { k: 420, z: .72 };
  var TRAIL = { k: 170, z: .95 };

  function box(a){
    var r = a.getBoundingClientRect(), o = rail.getBoundingClientRect();
    return vertical
      ? { s: r.top - o.top + rail.scrollTop,  e: r.bottom - o.top + rail.scrollTop }
      : { s: r.left - o.left + rail.scrollLeft, e: r.right - o.left + rail.scrollLeft };
  }

  function draw(){
    var len = Math.max(0, B.x - A.x);
    /* 늘어난 만큼 가늘어지고, 눌린 만큼 굵어진다 — 고무의 부피를 조금만 흉내 낸다 */
    var rest = Math.max(1, B.t - A.t);
    var k = len / rest - 1;
    var thin = 1 - Math.max(-.06, Math.min(.08, k * .06));
    if(vertical){
      blob.style.transform = 'translate3d(0,' + A.x + 'px,0) scaleX(' + thin.toFixed(4) + ')';
      blob.style.height = len + 'px';
      blob.style.width = '';
      paintText();
    } else {
      blob.style.transform = 'translate3d(' + A.x + 'px,0,0)';
      blob.style.width = len + 'px';
      blob.style.height = '';
    }
  }

  /* 덩어리가 링크 가운데를 덮고 있으면 그 링크만 흰 글자 — 지나가는 칸도 잠깐 희다 */
  function paintText(){
    for(var i=0;i<links.length;i++){
      var b = links[i].__box;
      if(!b) continue;
      var m = (b.s + b.e) / 2;
      links[i].classList.toggle('on-blob', A.x <= m && m <= B.x);
    }
  }
  function measureAll(){
    for(var i=0;i<links.length;i++) links[i].__box = vertical ? box(links[i]) : null;
  }
  function clearText(){
    for(var i=0;i<links.length;i++) links[i].classList.remove('on-blob');
  }

  function stepSpring(p, cfg, dt){
    var c = 2 * cfg.z * Math.sqrt(cfg.k);
    p.v += (cfg.k * (p.t - p.x) - c * p.v) * dt;
    p.x += p.v * dt;
  }

  function tick(now){
    raf = 0;
    var dt = Math.min(.05, (now - (last || now)) / 1000);
    last = now;
    var down = (A.t + B.t) / 2 >= (A.x + B.x) / 2;   /* 어느 쪽으로 가는가 */
    var n = Math.max(1, Math.ceil(dt / (1/120)));
    for(var i=0;i<n;i++){
      stepSpring(A, down ? TRAIL : LEAD, dt / n);
      stepSpring(B, down ? LEAD : TRAIL, dt / n);
      /* 뒤집히지 않게 — 덩어리 길이는 0 아래로 내려가지 않는다 */
      if(B.x < A.x){ var mid = (A.x + B.x) / 2; A.x = B.x = mid; }
    }
    draw();
    var rest = Math.abs(A.t - A.x) < .3 && Math.abs(B.t - B.x) < .3 &&
               Math.abs(A.v) < 4 && Math.abs(B.v) < 4;
    if(rest){ snap(); return; }
    raf = requestAnimationFrame(tick);
  }

  function snap(){
    if(raf){ cancelAnimationFrame(raf); raf = 0; }
    A.x = A.t; B.x = B.t; A.v = B.v = 0;
    last = 0;
    draw();
  }

  function aim(jump){
    if(hiddenMq.matches || !cur){ blob.style.opacity = '0'; return; }
    vertical = bigMq.matches;
    rail.classList.toggle('is-row', !vertical);
    var b = box(cur);
    A.t = b.s; B.t = b.e;
    if(vertical) measureAll(); else clearText();
    blob.style.opacity = '';
    if(jump || !placed || calmMq.matches){ placed = true; snap(); return; }
    if(!raf){ last = 0; raf = requestAnimationFrame(tick); }
  }

  function grpOf(a){ return a ? a.closest('.sf-grp') : null; }

  function sync(){
    var next = rail.querySelector('a[aria-current="true"]');
    if(next === cur) return;
    var prev = cur;
    cur = next;
    /* 가로 탭은 묶음마다 탭 줄이 갈린다 — 옛 자리가 의미 없으니 뛰지 않는다 */
    var jump = !bigMq.matches && grpOf(prev) !== grpOf(next);
    /* 가로 탭에서 묶음이 갈리는 순간 display 가 바뀐다 — 다음 그림에 잰다 */
    if(jump) requestAnimationFrame(function(){ aim(true); });
    else aim(false);
  }

  new MutationObserver(sync).observe(rail, { subtree: true, attributes: true, attributeFilter: ['aria-current'] });

  /* 폭 · 글(영문 보기) · 글꼴이 바뀌면 칸 크기가 달라진다 — 제자리에 다시 놓는다 */
  function replace(){ if(cur) aim(true); }
  if(window.ResizeObserver){
    var ro = new ResizeObserver(replace);
    ro.observe(rail);
    links.forEach(function(a){ ro.observe(a); });
  } else window.addEventListener('resize', replace);
  [bigMq, hiddenMq].forEach(function(mq){
    if(mq.addEventListener) mq.addEventListener('change', replace); else mq.addListener(replace);
  });
  if(document.fonts && document.fonts.ready) document.fonts.ready.then(replace);

  sync();
})();

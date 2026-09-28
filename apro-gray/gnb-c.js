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
      mega.classList.add('open');
      mega.setAttribute('aria-hidden', 'false');
    }
    if(typeof i === 'number') mark(i);
  }
  function close(){
    clearTimeout(t);
    if(!isOpen) return;
    isOpen = false;
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

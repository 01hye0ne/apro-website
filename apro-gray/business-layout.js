/* APRO 사업영역 서브페이지 공용 스크립트 — GNB / 오버레이 / 세로 캐러셀 */
/* GNB: lang dropdown + mega menu + light/dark contrast over hero */
(function(){
  var g=document.querySelector('.gnb-group');if(!g)return;
  var lb=document.getElementById('langBtn');
  if(lb){
    lb.addEventListener('click',function(e){e.stopPropagation();g.classList.toggle('lang-open');});
    document.addEventListener('click',function(e){if(!g.contains(e.target))g.classList.remove('lang-open');});
  }
  var nl=g.querySelectorAll('.gnb .menus a[data-i]');
  nl.forEach(function(a){a.addEventListener('mouseenter',function(){nl.forEach(function(x){x.classList.toggle('active',x===a);});});});
  var m=g.querySelector('.gnb .menus');
  if(m){
    m.addEventListener('mouseenter',function(){g.classList.add('mega-open');});
    g.addEventListener('mouseleave',function(){g.classList.remove('mega-open');nl.forEach(function(x){x.classList.remove('active');});});
  }
  var hero=document.querySelector('.dhero'),on=null;
  function ap(){var d=hero.getBoundingClientRect().bottom<=40;if(d!==on){on=d;g.classList.toggle('nav-light',d);}}
  var t=false;
  window.addEventListener('scroll',function(){if(!t){t=true;requestAnimationFrame(function(){t=false;ap();});}},{passive:true});
  window.addEventListener('resize',ap);ap();
  document.addEventListener('keydown',function(e){if(e.key==='Escape')g.classList.remove('lang-open');});
})();

/* hamburger -> overlay */
(function(){
  var b=document.querySelector('.menu-toggle'),o=document.getElementById('navover');
  if(!b||!o)return;
  var c=o.querySelector('.ov-close');
  function open(){o.classList.add('open');o.setAttribute('aria-hidden','false');b.setAttribute('aria-expanded','true');document.documentElement.style.overflow='hidden';}
  function close(){o.classList.remove('open');o.setAttribute('aria-hidden','true');b.setAttribute('aria-expanded','false');document.documentElement.style.overflow='';}
  b.addEventListener('click',open);
  if(c)c.addEventListener('click',close);
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&o.classList.contains('open'))close();});
})();

/* 소분류 위치 눈금 — 섹션 수를 세어 자동 생성. 소분류가 늘거나 줄어도 따라감 */
(function(){
  var secs=[].slice.call(document.querySelectorAll('.hsec'));
  secs.forEach(function(s,i){
    var c=s.querySelector('.heyebrow .cnt');
    if(!c)return;
    c.innerHTML='';
    c.setAttribute('role','img');   // 눈금은 그림이므로 대체 텍스트로 의미를 전달
    c.setAttribute('aria-label','소분류 '+secs.length+'개 중 '+(i+1)+'번째');
    for(var k=0;k<secs.length;k++){
      var t=document.createElement('i');
      t.className='tick'+(k===i?' on':'');
      c.appendChild(t);
    }
  });
})();

/* 세로 캐러셀
   - 하단 인덱스 자동 생성 + 클릭 이동
   - 휠 1회 = 카드 1장. 섹션의 카드를 다 넘긴 뒤에야 페이지가 다음 섹션으로 이동
   - 휠 리스너는 window에 건다. 섹션에 걸면 컨테이너(최대 1392px) 바깥 좌우 여백에
     커서가 있을 때 이벤트가 잡히지 않아 페이지가 그냥 스크롤돼 버린다. */
(function(){
  var narrow=window.matchMedia('(max-width:900px)');

  /* ── 스크롤 감도 조절값 ───────────────────────────────
     LERP   : 카드 스크롤이 매 프레임 목표값에 접근하는 비율. 낮을수록 여운이 길다
     SETTLE : 휠이 멎고 이 시간(ms) 뒤 가장 가까운 카드로 정렬
     THRESH : 카드 간격의 이 비율만큼 움직이면 다음 장으로 확정
     PAGE   : 섹션 → 섹션 이동 시간(ms)
     REARM  : 섹션 이동 후 휠 입력이 이만큼 멎어야 다음 동작을 받음 */
  var LERP=0.16, SETTLE=140, THRESH=0.25, PAGE=820, REARM=180;

  var states=[],raf=null,active=null,settleT=null;
  var paging=false,pageRaf=null,secArmed=true,secQuiet=null;

  document.querySelectorAll('.hsec').forEach(function(sec){
    var track=sec.querySelector('.htrack'),nav=sec.querySelector('.hnav');
    if(!track)return;
    var cards=[].slice.call(track.querySelectorAll('.hcard'));
    var st={sec:sec,track:track,cards:cards,idx:0,btns:[],pos:0,target:0,dir:1};

    if(cards.length<2){
      track.dataset.one='true';
      if(nav)nav.dataset.one='true';
    }else if(nav){
      cards.forEach(function(c,i){
        var b=document.createElement('button');
        b.type='button';
        b.className='hnav-i'+(i?'':' is-on');
        b.setAttribute('aria-label',c.dataset.tab||('카드 '+(i+1)));
        b.innerHTML='<span class="t">'+(c.dataset.tab||'')+'</span>';
        b.addEventListener('click',function(){goTo(st,i);});
        nav.appendChild(b);
      });
      st.btns=[].slice.call(nav.children);
    }

    /* 트랙을 직접(터치·드래그) 스크롤한 경우 현재 카드 추적 */
    track.addEventListener('scroll',function(){
      if(raf)return;   // JS가 움직이는 중에는 건너뜀
      st.pos=st.target=track.scrollTop;
      var best=0,bd=Infinity;
      cards.forEach(function(c,i){var d=Math.abs(c.offsetTop-track.scrollTop);if(d<bd){bd=d;best=i;}});
      if(best!==st.idx){st.idx=best;paint(st);}
    },{passive:true});

    states.push(st);
  });

  function paint(st){st.btns.forEach(function(b,i){b.classList.toggle('is-on',i===st.idx);});}
  function maxOf(st){return st.track.scrollHeight-st.track.clientHeight;}

  /* 목표값을 향해 매 프레임 남은 거리의 LERP만큼 이동.
     휠 입력이 목표값을 조금씩 밀어내고 화면은 그 뒤를 따라가므로,
     한 틱에 한 장이 통째로 넘어가지 않고 입력에 비례해 이어져 흐른다. */
  function loop(){
    var st=active;
    if(!st){raf=null;return;}
    var d=st.target-st.pos;
    if(Math.abs(d)<0.4){st.pos=st.target;st.track.scrollTop=st.pos;raf=null;return;}
    st.pos+=d*LERP;
    st.track.scrollTop=st.pos;
    raf=requestAnimationFrame(loop);
  }
  function kick(st){active=st;if(!raf)raf=requestAnimationFrame(loop);}

  function goTo(st,i){
    st.idx=Math.max(0,Math.min(st.cards.length-1,i));
    paint(st);
    st.pos=st.track.scrollTop;
    st.target=st.cards[st.idx].offsetTop;
    kick(st);
  }

  /* 휠이 멎으면 카드 경계로 정렬. 진행 방향으로 카드 간격의 THRESH 이상 왔으면 다음 장으로 */
  function settle(st){
    var step=st.cards[1].offsetTop-st.cards[0].offsetTop;
    var raw=st.target/step,base=Math.floor(raw),frac=raw-base;
    goTo(st, st.dir>0 ? (frac>THRESH?base+1:base) : (frac<1-THRESH?base:base+1));
  }

  /* 화면 세로 중앙을 점유한 섹션 = 지금 보고 있는 섹션 (커서 위치와 무관) */
  function current(){
    var mid=window.innerHeight/2;
    for(var i=0;i<states.length;i++){
      var r=states[i].sec.getBoundingClientRect();
      if(r.top<=mid&&r.bottom>=mid)return states[i];
    }
    return null;
  }

  /* ── 섹션 간 이동 — 카드 전환과 같은 easeInOutSine으로 직접 애니메이션.
        브라우저 CSS 스냅은 지속시간·이징을 제어할 수 없어 자석처럼 끌리는 느낌이 난다 ── */
  function ease(p){return .5-.5*Math.cos(Math.PI*p);}
  function armSec(){clearTimeout(secQuiet);secQuiet=setTimeout(function(){secArmed=true;},REARM);}
  function topOf(st){return window.scrollY+st.sec.getBoundingClientRect().top;}
  function pageTo(y){
    y=Math.max(0,Math.min(document.documentElement.scrollHeight-window.innerHeight,y));
    var from=window.scrollY,delta=y-from,t0=0;
    if(Math.abs(delta)<1)return;
    paging=true;
    cancelAnimationFrame(pageRaf);
    (function step(){
      pageRaf=requestAnimationFrame(function(ts){
        if(!t0)t0=ts;
        var p=Math.min(1,(ts-t0)/PAGE);
        window.scrollTo(0,from+delta*ease(p));
        if(p<1)step();
        else{paging=false;pageRaf=null;}
      });
    })();
  }

  /* 휠 가로채기
     - 섹션 안: 델타를 1:1로 트랙 목표값에 더해 카드가 입력을 따라 흐른다
     - 카드 끝: 이웃 섹션으로 pageTo() 애니메이션 (한 제스처에 한 섹션) */
  window.addEventListener('wheel',function(e){
    if(narrow.matches||!e.deltaY)return;
    armSec();                                    // 입력이 이어지는 동안 재무장을 미룸
    if(paging){e.preventDefault();return;}       // 섹션 이동 중에는 입력을 받지 않음

    var dir=e.deltaY>0?1:-1;
    var st=current(),i=states.indexOf(st);

    if(!st){                                     // 히어로 영역 — 아래로 굴리면 첫 섹션으로
      if(dir>0&&states.length){
        e.preventDefault();
        if(!secArmed)return;
        secArmed=false;pageTo(topOf(states[0]));
      }
      return;                                    // 위로는 기본 스크롤(맨 위)
    }

    var top=st.sec.getBoundingClientRect().top;
    if(Math.abs(top)>24){                        // 섹션이 어긋나 있으면 먼저 정렬시킨다
      e.preventDefault();
      if(!secArmed)return;
      secArmed=false;pageTo(window.scrollY+top);
      return;
    }

    if(!raf||active!==st){st.pos=st.target=st.track.scrollTop;}   // 유휴 상태면 실제 위치와 동기화
    var max=maxOf(st);
    var atEdge=st.cards.length<2||max<=0||(dir>0?st.target>=max-0.5:st.target<=0.5);

    if(!atEdge){                                 // ── 카드 스크롤 ──
      e.preventDefault();
      if(!secArmed)return;                       // 섹션 이동 직후 관성으로 카드가 밀리는 것 방지
      st.dir=dir;
      st.target=Math.max(0,Math.min(max,st.target+e.deltaY));
      kick(st);
      clearTimeout(settleT);
      settleT=setTimeout(function(){settle(st);},SETTLE);
      return;
    }

    /* ── 카드 끝 → 이웃 섹션 ── */
    var nx=dir>0?i+1:i-1,y=null;
    if(nx>=0&&nx<states.length)y=topOf(states[nx]);
    else if(dir<0)y=0;                           // 첫 섹션 위로 → 히어로
    if(y===null)return;                          // 마지막 섹션 아래 → 기본 스크롤에 맡김
    e.preventDefault();
    if(!secArmed)return;
    secArmed=false;pageTo(y);
  },{passive:false});
})();

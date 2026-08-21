/* APRO 사업영역 서브페이지 공용 스크립트 — 카드 진입 연출 / GNB / 오버레이 / 세로 캐러셀 */

/* 카드 진입 스태거
   카드가 화면 가운데 대역에 들어오면 구성 요소를 순서대로 내려앉힌다.
   휠은 건드리지 않는다 — 카드 안에서 스크롤을 소비하면 굴려도 화면이 안 움직여
   멈춘 것처럼 읽히고, 이 페이지는 이미 휠을 카드 이동·섹션 이동에 두 번 쓰고 있다.
   한 번 나타난 카드는 되감지 않는다. 오갈 때마다 재생되면 산만하다.

   초기 숨김(.rv)은 <head> 부트스트랩이 html[data-reveal]을 붙였을 때만 걸리므로
   이 모듈이 못 돌면 내용이 영영 안 보인다 → 파일 맨 앞에 두어 뒤쪽 오류의 영향을 끊는다 */
(function(){
  var root=document.documentElement;
  if(!root.hasAttribute('data-reveal'))return;
  var cards=[].slice.call(document.querySelectorAll('.hcard'));
  if(!cards.length){root.removeAttribute('data-reveal');return;}

  /* 통째로 두면 덩어리째 튀어나와 밋밋한 묶음 — 안쪽 항목을 하나씩 떨군다.
     특히 공정 순서 7단계는 왼쪽부터 차례로 떨어져야 순서라는 의미가 같이 읽힌다 */
  /* hdeck-top 은 .hcard--deck 이 본문을 한 번 감싼 묶음이다 — 감싼 채로 두면 제목과
     문단이 한 덩어리로 같이 뜨므로, 안쪽을 풀어 종전처럼 한 줄씩 떨어지게 한다 */
  var SPLIT=[['fsteps','li'],['hthumbs','.th'],['hlead',':scope>*'],
             ['hgrid2','.cell'],['hcols2',':scope>*'],['gmap',':scope>*'],
             ['hdeck-top',':scope>*']];
  var STEP=60, SUB=36;   /* 최상위 단위 간격 / 묶음 안쪽 간격 (ms) */

  function mark(el,d){el.classList.add('rv');el.style.setProperty('--rd',d+'ms');}

  cards.forEach(function(card){
    var t=0;
    [].slice.call(card.children).forEach(function(el){
      var sel=null;
      for(var i=0;i<SPLIT.length;i++){
        if(el.classList.contains(SPLIT[i][0])){sel=SPLIT[i][1];break;}
      }
      var parts=sel?[].slice.call(el.querySelectorAll(sel)):[];
      if(parts.length){
        parts.forEach(function(p){mark(p,t);t+=SUB;});
        t+=STEP-SUB;                       /* 묶음이 끝나면 원래 간격으로 되돌린다 */
      }else{
        mark(el,t);t+=STEP;
      }
    });
  });

  /* 화면 세로 가운데 70% 대역에 걸치면 시작.
     트랙 아래로 살짝 보이는 다음 카드(80px)는 이 대역 밖이라 미리 재생되지 않는다 */
  var io=new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(!e.isIntersecting)return;
      e.target.classList.add('is-in');
      io.unobserve(e.target);              /* 한 번만 */
    });
  },{rootMargin:'-15% 0px -15% 0px'});
  cards.forEach(function(c){io.observe(c);});
})();

/* GNB: lang dropdown + mega menu + light/dark contrast over hero */
(function(){
  var g=document.querySelector('.gnb-group');if(!g)return;
  var lb=document.getElementById('langBtn');
  if(lb){
    lb.addEventListener('click',function(e){e.stopPropagation();g.classList.toggle('lang-open');});
    document.addEventListener('click',function(e){
      if(g.contains(e.target))return;
      g.classList.remove('lang-open');paintNav();   // 메뉴가 닫혔으니 접힘 여부를 다시 판정
    });
  }
  var nl=g.querySelectorAll('.gnb .menus a[data-i]');
  nl.forEach(function(a){a.addEventListener('mouseenter',function(){nl.forEach(function(x){x.classList.toggle('active',x===a);});});});
  var m=g.querySelector('.gnb .menus');
  if(m){
    m.addEventListener('mouseenter',function(){g.classList.add('mega-open');});
    g.addEventListener('mouseleave',function(){
      g.classList.remove('mega-open');nl.forEach(function(x){x.classList.remove('active');});
      paintNav();   // 메가가 닫혔으니 접힘 여부를 다시 판정
    });
  }
  /* 한동안 여기서 .chero(콘텐츠 페이지의 낮은 띠 히어로)도 함께 찾았다. 2026-08-21
     에 투자정보·지속가능경영·커뮤니티 아홉 장이 세부 페이지와 같은 .dhero + .bnav-wrap
     으로 갈아타면서 그 클래스가 사이트에서 사라져 선택자를 되돌린다 */
  var hero=document.querySelector('.dhero'),bn=document.querySelector('.bnav-wrap'),
      cn=document.querySelector('.cnav-wrap'),   /* 회사소개 목차 탭 바 (아래 ap 참고) */
      ft=document.querySelector('.footer'),on=null,hid=null;
  var narrowMq=window.matchMedia('(max-width:900px)');
  /* 기준선 = --bar-top + --bar-rise + --bar-h (= 고정됐을 때 바의 밑변 y).
     바의 실측 높이(offsetHeight)를 쓸 수 없다 — 고정되면 위로 늘어나 값이 커지고,
     되올릴 때 기준선이 같이 밀려 히스테리시스가 생긴다. CSS 변수를 그대로 읽는다 */
  var barBase=104;
  function measure(){
    var cs=getComputedStyle(document.documentElement);
    var h=parseFloat(cs.getPropertyValue('--bar-h')),
        r=parseFloat(cs.getPropertyValue('--bar-rise')),
        t=parseFloat(cs.getPropertyValue('--bar-top'));
    if(h)barBase=h+(r||0)+(t||0);
  }

  /* GNB 접기/꺼내기
     넓은 화면에서 탭 바가 고정되면 GNB 자리를 어두운 바가 채우므로 GNB를 접는다.
     대신 화면 맨 위 HOT px 안에 커서가 들어오면 다시 꺼낸다 — 접힌 뒤에도 로고·전체메뉴로
     돌아갈 길을 남겨야 하기 때문. 메가·언어 메뉴가 열려 있으면 커서가 띠를 벗어나도
     접지 않는다(메가 패널은 띠 아래까지 내려오므로 그때 접으면 메뉴가 사라진다).
     좁은 화면은 호버가 없는 터치 기기가 대부분이라 애초에 접지 않고, 바가 GNB 아래로 붙는다 */
  var HOT=72,hotIn=false;
  function paintNav(){
    var keep=hotIn||g.classList.contains('mega-open')||g.classList.contains('lang-open');
    g.classList.toggle('nav-hide',!!hid&&!keep);
    /* 회사소개(.cnav-*)는 제 탭 바를 따로 굴리지만 GNB 를 접었다 꺼내는 판정은 이것을
       그대로 쓴다 → '지금 꺼내야 하는 상태'만 문서에 걸어 두고 그쪽 CSS 가 받아 간다 */
    document.documentElement.classList.toggle('nav-peek',keep);
  }
  document.addEventListener('mousemove',function(e){
    var v=e.clientY<=HOT;
    if(v===hotIn)return;   /* 띠를 드나들 때만 다시 칠한다 */
    hotIn=v;paintNav();
  },{passive:true});

  function ap(){
    /* 히어로가 없는 페이지도 있다(글로벌 네트워크 — 어두운 지도 한 장이 곧 첫 화면).
       그때는 히어로 밑변이 화면 밖 저 아래에 있는 셈 치면 된다 → 흰 플레이트를 깔지
       않고 GNB 글자도 흰색 그대로 남아, 어두운 바닥 위에서 그대로 읽힌다 */
    var hb=hero?hero.getBoundingClientRect().bottom:Infinity;
    /* 소분류 탭 바는 히어로 밑단에 얹혀 있다가, 히어로 밑변이 바 밑변에 닿는 순간
       고정된다. 그 순간 탭 띠 위치가 그대로라 화면이 안 튄다.
       0.5px 여유는 소수점 스크롤 위치에서 붙었다 떨어졌다 하는 떨림을 막는다 */
    var h=!!bn&&hb<=barBase+0.5;
    /* 회사소개(.cnav-wrap)는 제 탭 바를 따로 굴리지만 — 두 상태 사이 생김새가 달라
       공용 규칙에 얹히지 않는다 — 고정되는 시점과 그때의 바는 이 바와 같다.
       GNB 를 접고 꺼내는 판정도 그래서 같이 본다 (아래 want·d 가 fx 를 쓴다) */
    var fx=(!!bn||!!cn)&&hb<=barBase+0.5;
    /* GNB 흰 플레이트는 GNB 뒤가 흰 본문일 때만 — 넓은 화면에서 바가 고정되면
       GNB 자리가 어두운 바라서 플레이트를 깔면 안 된다 */
    var nar=narrowMq.matches;
    var d=hb<=40&&!(fx&&!nar);
    if(d!==on){on=d;g.classList.toggle('nav-light',d);}
    if(!bn){
      /* 회사소개는 여기서 끝 — 바 자체(.is-fixed)는 그 페이지 스크립트가 붙인다 */
      var w2=fx&&!nar;
      if(w2!==hid){hid=w2;if(w2)g.classList.remove('mega-open','lang-open');paintNav();}
      return;
    }
    bn.classList.toggle('is-fixed',h);
    /* 푸터를 반 넘게 드러냈으면 바를 접어 올린다 — 거기서부터는 푸터를 읽는 중이고
       소분류 탭은 볼 일이 없다. 푸터(553px)가 화면보다 낮아 밑변이 화면 위로 못 올라오므로
       "푸터 top 이 바 밑변에 닿으면"만으로는 큰 화면에서 아예 발동하지 않는다.
       그래도 화면이 낮아 실제로 겹치는 경우가 있으니 그 조건도 OR 로 남겼다.
       매 스크롤 프레임에서 다시 판정해야 하므로 아래 상태 변화 조기 반환보다 먼저 둔다 */
    var away=false;
    if(h&&ft){
      var fr=ft.getBoundingClientRect(),shown=window.innerHeight-fr.top;
      away=shown>=fr.height/2||fr.top<=barBase+0.5;
    }
    bn.classList.toggle('is-away',away);
    var want=h&&!nar;
    if(want===hid)return;
    hid=want;
    if(want)g.classList.remove('mega-open','lang-open');   // 접히면서 열려 있던 메뉴도 닫는다
    paintNav();
  }
  var t=false;
  window.addEventListener('scroll',function(){if(!t){t=true;requestAnimationFrame(function(){t=false;ap();});}},{passive:true});
  window.addEventListener('resize',function(){measure();ap();});
  measure();ap();
  document.addEventListener('keydown',function(e){if(e.key==='Escape'){g.classList.remove('lang-open');paintNav();}});
})();

/* 푸터 패밀리사이트 드롭다운 (apro-gray/index.html 과 같은 동작) */
(function(){
  var fam=document.getElementById('fFamily');
  if(!fam)return;
  var btn=fam.querySelector('.fbtn');
  btn.addEventListener('click',function(e){
    e.stopPropagation();
    var open=fam.classList.toggle('open');
    btn.setAttribute('aria-expanded',open?'true':'false');
  });
  function close(){fam.classList.remove('open');btn.setAttribute('aria-expanded','false');}
  document.addEventListener('click',function(e){if(!fam.contains(e.target))close();});
  document.addEventListener('keydown',function(e){if(e.key==='Escape')close();});
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

/* 세로 캐러셀
   - 하단 스크롤 게이지(스크롤바 역할: 표시 + 클릭·키보드 이동)
   - 상단 소분류 탭: 클릭하면 섹션 이동, 스크롤하면 현재 섹션에 표시
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

  /* 좌측 레일 카드 인덱스 — 카드의 data-tab 을 그대로 목록으로 펼친다.
     예전 하단 스크롤 게이지가 겸했던 "몇 장 중 어디쯤인가"와 "카드 이동"을 함께 받는다.
     HTML 에 손으로 적지 않는 이유 — 카드가 늘거나 제목이 바뀌면 목록이 어긋나고,
     A/A-1 여덟 페이지가 같은 목록을 두 번 관리하게 된다.
     data-tab 이 없는 카드는 h3 글자로 대신한다 */
  function buildIndex(sec,rail,track,cards,st){
    if(!track.id)track.id=(sec.id||'hsec')+'-track';
    var ol=document.createElement('ol');
    ol.className='hidx';
    /* 소분류 타이틀은 <br> 로 줄을 나눠 놓았다 — textContent 는 그 자리를 그냥 이어붙여
       "이차전지 활성화전공정 설비" 가 되므로, 줄바꿈을 공백으로 주는 innerText 를 쓴다 */
    var ttl=sec.querySelector('.httl');
    var name=ttl?(ttl.innerText||ttl.textContent).replace(/\s+/g,' ').trim()+' ':'';
    ol.setAttribute('aria-label',name+'카드 '+cards.length+'장');
    var btns=cards.map(function(c,i){
      var h3=c.querySelector('h3');
      var li=document.createElement('li');
      var b=document.createElement('button');
      b.type='button';
      b.textContent=c.dataset.tab||(h3?h3.textContent:'카드 '+(i+1));
      b.setAttribute('aria-controls',track.id);
      b.addEventListener('click',function(){goTo(st,i);});
      li.appendChild(b);ol.appendChild(li);
      return b;
    });
    rail.appendChild(ol);
    return btns;
  }

  /* 바 오른쪽 끝 소속 뱃지 — HTML 에서 .hrail 바로 밑에 적어 둔 .hbadge(예: 이차전지
     소재의 "에이프로 머티리얼즈")를 목록 안 마지막 항목으로 옮긴다. 패밀리 사이트로
     나가는 링크라 카드가 아니라 소분류에 걸리는 꼬리표이고, 그래서 카드 마크업이 아니라
     레일에 적는다. 복제가 아니라 이동이다 — 같은 말이 DOM 에 두 번 있으면 읽기 도구가
     두 번 읽는다.
     ol 안으로 넣는 이유는 오른쪽 끝 정렬(margin-left:auto) 때문이다. 레일에 형제로
     두면 바(=ol) 바깥이라 바 안쪽 끝에 설 수가 없다.
     ol 이 없는 소분류(카드가 하나뿐이라 목록을 안 만든 경우)는 그냥 레일에 남는다 —
     파란 바가 없는 자리이니 뱃지 기본 생김새(파란 채움) 그대로 읽힌다 */
  function placeBadge(rail,sec){
    var badge=rail.querySelector(':scope > .hbadge');
    if(!badge)return;
    /* 2026-08-11 레이아웃 — 뱃지를 카드 제목 옆에 단다. 인덱스가 가로 바에서
       세로 목록으로 바뀌면서, 바 오른쪽 끝에 붙던 이 꼬리표가 목록 옆에 혼자
       떠 보이게 됐다. 뱃지는 "이 소분류를 어느 계열사가 만드는가"라 소분류 단위
       정보인데, 카드는 한 번에 한 장만 보이므로 제목마다 하나씩 둔다 —
       첫 장에는 원본을, 나머지에는 복제를 넣고 복제는 보조기술·탭 이동에서 뺀다
       (같은 링크가 여러 번 읽히지 않게).
       한동안 A(!.v-a1)에서만 이렇게 했다 — A-1 은 파란 가로 바를 그대로 쓰고
       있었기 때문이다. 세부 페이지 네 개가 모두 두 시안에서 세로 목록을 쓰게 된
       뒤(같은 날) 그 분기를 걷었다. 아래 ol 경로는 이제 목록 자체가 없는 소분류
       (카드 한 장)에서만 쓰인다 */
    if(sec){
      var hs=sec.querySelectorAll('.hcard h3');
      if(hs.length){
        for(var i=0;i<hs.length;i++){
          if(i===0){hs[i].appendChild(badge);continue;}
          var c=badge.cloneNode(true);
          c.setAttribute('tabindex','-1');
          c.setAttribute('aria-hidden','true');
          hs[i].appendChild(c);
        }
        return;
      }
    }
    var ol=rail.querySelector('ol.hidx');
    if(!ol)return;
    var li=document.createElement('li');
    li.className='hidx-badge';
    li.appendChild(badge);
    ol.appendChild(li);
  }

  document.querySelectorAll('.hsec').forEach(function(sec){
    var track=sec.querySelector('.htrack'),rail=sec.querySelector('.hrail');
    if(!track)return;
    var cards=[].slice.call(track.querySelectorAll('.hcard'));
    var st={sec:sec,track:track,cards:cards,idx:0,btns:[],cur:-1,pos:0,target:0,dir:1};

    /* 카드가 하나면 넘길 것도, 목록이 될 것도 없다 */
    if(cards.length<2)track.dataset.one='true';
    else if(rail)st.btns=buildIndex(sec,rail,track,cards,st);
    /* buildIndex 밖에서 부른다 — 카드가 하나뿐이라 목록을 HTML 에 손으로 적어 둔
       소분류(예: 반도체 GaN 두 곳)도 같은 자리에 뱃지를 걸 수 있어야 한다 */
    if(rail)placeBadge(rail,sec);

    /* 트랙을 직접(터치·드래그) 스크롤한 경우 현재 카드 추적.
       JS가 움직일 때도 매 프레임 여기로 들어오므로 게이지는 먼저 갱신한다 */
    track.addEventListener('scroll',function(){
      paint(st);
      if(raf)return;   // JS가 움직이는 중에는 건너뜀
      st.pos=st.target=track.scrollTop;
      var best=0,bd=Infinity;
      cards.forEach(function(c,i){var d=Math.abs(c.offsetTop-track.scrollTop);if(d<bd){bd=d;best=i;}});
      st.idx=best;
    },{passive:true});

    states.push(st);
  });

  /* 인덱스의 현재 항목 = 트랙 스크롤 위치에 가장 가까운 카드.
     st.idx(휠·클릭이 확정한 목표)를 그대로 쓰지 않는 이유가 둘 있다 —
     움직이는 중에도 눈에 보이는 카드를 따라가야 하고, 터치로 트랙을 직접 스크롤하면
     아래 scroll 핸들러가 raf 중에는 st.idx 를 갱신하지 않는다.
     값이 그대로면 DOM 을 건드리지 않는다 → 매 프레임 불려도 부담이 없다 */
  function paint(st){
    if(!st.btns.length)return;
    var top=st.track.scrollTop,best=0,bd=Infinity;
    st.cards.forEach(function(c,i){
      var d=Math.abs(c.offsetTop-top);
      if(d<bd){bd=d;best=i;}
    });
    if(best===st.cur)return;
    st.cur=best;
    st.btns.forEach(function(b,i){
      if(i===best)b.setAttribute('aria-current','true');
      else b.removeAttribute('aria-current');
    });
  }
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

    /* 섹션 밖 — 위쪽(히어로)인지 아래쪽(푸터)인지 갈라야 한다.
       예전에는 둘 다 "히어로"로 보고 아래로 굴리면 첫 섹션으로 보냈는데,
       푸터가 생긴 뒤로는 푸터에서 아래로 굴렸을 때 맨 위로 튀어 올라가 버린다 */
    if(!st){
      var first=states[0],last=states[states.length-1];
      if(!first)return;
      if(first.sec.getBoundingClientRect().top>window.innerHeight/2){
        if(dir>0){                               // 히어로 → 첫 섹션 (위로는 기본 스크롤)
          e.preventDefault();
          if(!secArmed)return;
          secArmed=false;pageTo(topOf(first));
        }
        return;
      }
      if(dir<0){                                 // 푸터 → 마지막 섹션 (아래로는 기본 스크롤)
        e.preventDefault();
        if(!secArmed)return;
        secArmed=false;pageTo(topOf(last));
      }
      return;
    }

    var top=st.sec.getBoundingClientRect().top;
    /* 마지막 섹션에서 카드를 다 넘긴 뒤 아래로 빠져나가는 중(= 푸터로 가는 길)인가?
       섹션 높이가 화면 한 칸이라 밑변이 화면 중앙을 지나기 전까지는 current() 가 계속
       이 섹션을 가리킨다. 그 구간을 아래 정렬 규칙이 되잡으면 굴려도 굴려도 푸터로
       못 내려간다 — 기본 스크롤로 내려간 만큼을 매번 top:0 으로 끌어올리기 때문. */
    var leaving=i===states.length-1&&dir>0&&top<=0&&
                (st.cards.length<2||st.track.scrollTop>=maxOf(st)-0.5);
    if(!leaving&&Math.abs(top)>24){               // 섹션이 어긋나 있으면 먼저 정렬시킨다
      e.preventDefault();
      if(!secArmed)return;
      secArmed=false;pageTo(window.scrollY+top);
      return;
    }
    if(leaving)return;                           // 푸터까지는 기본 스크롤에 맡긴다

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

  /* 게이지 초기값 — 카드 높이가 화면 높이에 따라 달라지므로 리사이즈 때 다시 그린다 */
  function repaint(){states.forEach(paint);}
  window.addEventListener('resize',repaint);
  window.addEventListener('load',repaint);
  repaint();

  /* ── 상단 소분류 탭 ──────────────────────────────────────────────────
     클릭은 섹션 간 이동과 같은 pageTo()를 태워 휠 이동과 느낌을 맞춘다(앵커 점프 금지).
     현재 탭 표시는 휠 핸들러의 current()와 같은 기준 — 화면 세로 중앙을 점유한 섹션 */
  (function(){
    var tabs=[].slice.call(document.querySelectorAll('.bnav-tabs a[href^="#"]'));
    if(!tabs.length)return;
    var secs=tabs.map(function(a){return document.getElementById(a.getAttribute('href').slice(1));});

    tabs.forEach(function(a,i){
      a.addEventListener('click',function(e){
        if(!secs[i]||narrow.matches)return;      // 좁은 화면은 기본 앵커 이동에 맡긴다
        e.preventDefault();
        pageTo(window.scrollY+secs[i].getBoundingClientRect().top);
      });
    });

    /* 탭 오른쪽 네모 페이지네이션 — 소분류 수만큼 만들어 바에 붙인다.
       소분류가 페이지마다 2~4개라 마크업이 아니라 여기서 만든다 (카드 안 다중
       이미지 막대를 그림 수만큼 만드는 것과 같은 방식). 자리·색은 CSS 의 .bnav-pager.
       클릭은 탭의 click() 을 그대로 태운다 → 섹션 이동이 휠·탭과 완전히 같아진다.
       현재 표시는 아래 spy() 가 탭과 한자리에서 함께 갱신하므로 판정 기준이 갈릴 일이 없다 */
    var pbtns=[];
    (function(){
      var bar=document.querySelector('.bnav');
      if(!bar||tabs.length<2)return;             // 소분류가 하나면 셀 것이 없다
      var pager=document.createElement('div');
      pager.className='bnav-pager';
      pbtns=tabs.map(function(a){
        var b=document.createElement('button');
        b.type='button';
        b.setAttribute('aria-label',(a.textContent||'').trim());
        b.addEventListener('click',function(){a.click();});
        pager.appendChild(b);
        return b;
      });
      bar.appendChild(pager);
    })();

    var on=-1;
    function spy(){
      var mid=window.innerHeight/2,k=-1;
      for(var i=0;i<secs.length;i++){
        if(!secs[i])continue;
        var r=secs[i].getBoundingClientRect();
        if(r.top<=mid&&r.bottom>=mid){k=i;break;}
      }
      if(k<0)k=(on<0?0:on);                      // 히어로 구간에서는 직전 표시를 유지
      if(k===on)return;
      on=k;
      tabs.forEach(function(a,i){
        if(i===k)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current');
        if(!pbtns[i])return;
        if(i===k)pbtns[i].setAttribute('aria-current','true');else pbtns[i].removeAttribute('aria-current');
      });
    }
    var tk=false;
    window.addEventListener('scroll',function(){
      if(tk)return;
      tk=true;requestAnimationFrame(function(){tk=false;spy();});
    },{passive:true});
    spy();
  })();
})();

/* 마을 진입 — 푸터 앞 '다른 사업영역' 픽토그램은 화면에 들어올 때 붙인다.
   선 그려지는 애니메이션이 SVG 파일 안에 들어 있는데, <img> 는 불러오는 순간
   딱 한 번 재생한다. 페이지 맨 아래에 있는 그림을 미리 불러 두면 스크롤해
   내려왔을 때 이미 다 끝나 있다 → src 를 이 시점에 붙여 그 자리에서 그려지게 한다.
   (그래서 마크업에는 src 가 아니라 data-src 로 들어 있다) */
(function(){
  var imgs=[].slice.call(document.querySelectorAll('.bhlot img[data-src]'));
  if(!imgs.length)return;
  var town=document.querySelector('.bhop-town');
  function load(){
    imgs.forEach(function(im){im.src=im.getAttribute('data-src');im.removeAttribute('data-src');});
    /* 태그 불 켜지는 루프도 여기서 함께 출발시킨다 — CSS 가 paused 로 잡아 두고 있다가
       이 클래스로 풀리고, --draw(선이 다 그려지는 시간)만큼 기다렸다 첫 불이 켜진다.
       둘을 같은 시점에 묶어야 그리기가 끝나자마자 불이 이어받는다 */
    if(town)town.classList.add('is-lit');
  }
  if(!town||!('IntersectionObserver' in window)){load();return;}  /* 못 쓰면 그냥 띄운다 */
  var io=new IntersectionObserver(function(es){
    if(!es[0].isIntersecting)return;
    load();io.disconnect();                /* 한 번만 */
  },{rootMargin:'0px 0px -12% 0px'});      /* 마을이 화면에 제대로 들어왔을 때 */
  io.observe(town);
})();

/* 여러 장짜리 비주얼 — 2초마다 다음 장으로
   그림이 둘 이상인 자리(.hph--slides)는 같은 칸에 겹쳐 두고 순서대로 넘긴다.
   몇 장인지·지금 몇 번째인지 알리는 하단 막대도 여기서 만든다 — 그림 수만큼 칸을
   찍어내므로 HTML 에 장수를 적어둘 필요가 없다(좌측 카드 인덱스와 같은 방식).

   화면 밖에서는 돌리지 않는다. 이 페이지는 카드가 세로 캐러셀로 쌓여 있어 한 번에
   한 장만 보이는데, 안 보이는 카드까지 계속 넘기면 돌아왔을 때 엉뚱한 장이 떠 있고
   타이머만 열 몇 개가 함께 돈다. 들어올 때 첫 장부터 다시 시작한다.

   움직임을 줄이는 설정(prefers-reduced-motion)이면 첫 장만 두고 넘기지 않는다.
   막대는 그대로 둔다 — "여러 장이 있다"는 정보 자체는 남아야 한다 */
(function(){
  var DELAY=2000;
  var slides=[].slice.call(document.querySelectorAll('.hph--slides'));
  if(!slides.length)return;
  var still=window.matchMedia&&window.matchMedia('(prefers-reduced-motion:reduce)').matches;

  var sets=slides.map(function(box){
    var imgs=[].slice.call(box.querySelectorAll('img'));
    if(imgs.length<2)return null;
    /* 첫 장은 지연 로딩을 풀어 둔다 — 카드가 보이는 순간 이미 떠 있어야 하고,
       뒷장들은 lazy 그대로 두면 넘어가는 순간 빈 칸이 스쳐 지나간다 → 함께 깨운다 */
    imgs.forEach(function(im){im.loading='eager';});
    imgs[0].classList.add('is-on');

    var bar=document.createElement('span');
    bar.className='hslide-bar';
    bar.setAttribute('aria-hidden','true');   /* 장식 — 그림 설명은 각 img 의 alt 가 한다 */
    var pips=imgs.map(function(_,i){
      var pip=document.createElement('i');
      if(!i)pip.className='is-on';
      bar.appendChild(pip);return pip;
    });
    box.appendChild(bar);
    return {box:box,imgs:imgs,pips:pips,i:0,timer:0};
  }).filter(Boolean);
  if(!sets.length)return;

  function show(st,n){
    st.imgs[st.i].classList.remove('is-on');st.pips[st.i].classList.remove('is-on');
    st.i=n;
    st.imgs[n].classList.add('is-on');st.pips[n].classList.add('is-on');
  }
  function start(st){
    if(still||st.timer)return;
    st.timer=setInterval(function(){show(st,(st.i+1)%st.imgs.length);},DELAY);
  }
  function stop(st,rewind){
    if(st.timer){clearInterval(st.timer);st.timer=0;}
    if(rewind&&st.i)show(st,0);
  }

  if(!('IntersectionObserver' in window)){sets.forEach(start);return;}
  var io=new IntersectionObserver(function(es){
    es.forEach(function(e){
      var st=sets.filter(function(s){return s.box===e.target;})[0];
      if(!st)return;
      if(e.isIntersecting)start(st);else stop(st,true);
    });
  },{threshold:.35});     /* 칸이 3분의 1 넘게 보이면 = 이 카드를 보고 있는 것 */
  sets.forEach(function(st){io.observe(st.box);});

  /* 탭을 덮어 두면 브라우저가 타이머를 몰아 처리한다 → 돌아왔을 때 여러 장이
     한꺼번에 스쳐 지나간다. 숨을 때 세우고 돌아올 때 다시 건다 */
  document.addEventListener('visibilitychange',function(){
    sets.forEach(function(st){
      if(document.hidden)stop(st,false);
      else if(st.box.getBoundingClientRect().top<innerHeight&&st.box.getBoundingClientRect().bottom>0)start(st);
    });
  });
})();

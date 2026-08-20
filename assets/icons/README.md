# 본문 소형 아이콘 세트

사업영역 세부 페이지의 카드 안 목록(`ul.pict > li > span.ic`)에 들어가는 아이콘이다.
사업영역을 대표하는 큰 픽토그램(`assets/vec-*.svg`)과는 다른 것이니 섞지 말 것.

## 지금 상태

이 폴더의 `*.svg` 40장은 **기존 페이지에서 그대로 뽑아낸 것**이다(as-is). 참고용이고,
아래 새 세트로 갈아탈 때 이름부터 바뀐다. 어느 파일이 어느 자리에 쓰이는지는
`_manifest.json` 에 들어 있다.

## 규격

| | 값 |
|---|---|
| 그리드 | 24 × 24 |
| 획 굵기 | 1.4 |
| 캡 / 조인 | round |
| 색 | `stroke="currentColor"` — 글자색을 따라간다 |
| 채움 | `fill="none"` |

라운드는 A 마크에서 가져온 두 값을 쓴다(라이브 영역 20 기준).

| | 비율 | 24 그리드 |
|---|---|---|
| R-조임 (획이 만나는 모서리) | 0.10 | 2 |
| R-열림 (봉우리·아치·캡) | 0.35 | 7 |

사선은 **1:3 기울기**(18.4°)로 통일한다 — 로고 다리의 18.21° 를 그리드에 맞춘 값이다.

⚠ 기존 40장은 28 그리드 · 획 1.6 이다(일부 24 · 1.4 가 섞여 있다). 새로 그릴 때
24 · 1.4 로 통일한다.

## 세트 — 8계열 42장

이름은 `계열-뜻` 꼴. 계열 접두어가 곧 묶음이라 폴더를 따로 두지 않는다.

### thermal — 열·온도 (2)
| 파일 | 쓰이는 자리 |
| --- | --- |
| `thermal-control` | 내부 온도 정밀 제어(UPS) · 열관리 설계(발사체) |
| `thermal-runaway` | 열 폭주·전이 방지(UPS) · 전해액 열분해 억제(LiFSI) |

### power — 전력·충방전 (7)
| 파일 | 쓰이는 자리 |
| --- | --- |
| `power-bidirectional` | 양방향 충·방전 |
| `power-regen` | 회생 에너지 회수 |
| `power-grid-return` | 전력망 반환 |
| `power-efficiency` | 전력 낭비·냉각 부하 저감 · 운영 효율 극대화 |
| `power-fast-charge` | 충전 시간 단축 · 고속 충전 성능 극대화 |
| `power-conversion` | 전력변환·제어 |
| `power-minimal` | 최소 전력 유지 |

### life — 수명·건강도 (5)
| 파일 | 쓰이는 자리 |
| --- | --- |
| `life-cycle` | 전체 수명 연장 · 배터리 수명 개선 |
| `life-soh` | 열화·SOH 평가 |
| `life-soh-fast` | 10분 내 SOH 예측 |
| `life-reuse` | 재사용 적합성 선별 |
| `life-circular` | ESS 이차 활용 |

### watch — 감시·진단 (7)
| 파일 | 쓰이는 자리 |
| --- | --- |
| `watch-realtime` | 온도·전압 정밀 제어 · 실시간 상태 모니터링 |
| `watch-analytics` | 실시간 모니터링 및 데이터 분석 |
| `watch-thermal` | 이상 온도 감시 |
| `watch-voltage` | 과전압·불균형 감시 |
| `watch-cell` | 이상 셀 조기 식별 |
| `watch-deviation` | 셀·모듈 편차 분석 |
| `watch-fault` | 이상 감지·보호 제어 |

### control — 제어·안전 (6)
| 파일 | 쓰이는 자리 |
| --- | --- |
| `control-precision` | 고도화된 BMS & BCP·BPU 시스템 |
| `control-balancing` | 셀 단위 온도·전압 밸런싱 제어 |
| `control-bypass` | 바이패스 기술(이상 셀 분리) |
| `control-interlock` | 안전 인터록 |
| `control-equipment` | 설비 제어 |
| `control-auth` | 인증·안전관리 |

### data — 생산·데이터 (6)
| 파일 | 쓰이는 자리 |
| --- | --- |
| `data-collect` | 데이터 수집 |
| `data-integration` | 데이터 통합 |
| `data-host-link` | 상위 연동 |
| `data-trace` | 생산 추적 |
| `data-recipe` | 레시피 하향 |
| `data-quality` | 품질 판정 |

### material — 소재·물성 (4)
| 파일 | 쓰이는 자리 |
| --- | --- |
| `material-resistance` | 내부 저항 저감 |
| `material-ionic` | 이온 전도도 향상 |
| `material-sei` | SEI 피막 형성 & 계면 저항 저감 |
| `material-volume` | 부피 팽창 / 입자 붕괴 억제 |

### build — 구조·하드웨어 (5)
| 파일 | 쓰이는 자리 |
| --- | --- |
| `build-shock` | 내진동·내충격 구조 설계 |
| `build-lightweight` | 저중량·저비용화 배터리팩 |
| `build-cost` | 발사체 탑재 효율·운용 경제성 향상 |
| `build-hardware` | 충전 하드웨어 |
| `build-comm` | 차량·충전기 통신 |

## as-is 40장에서 달라지는 것

**쪼갠 것 2** — 지금은 한 도형이 뜻이 다른 자리를 겸하고 있다.

- `내부 저항 저감`(소재 물성)이 `운영 효율`·`전력 낭비`(운영 지표)와 같은 그림을
  쓰고 있었다 → `material-resistance` 로 분리
- `이상 온도 감시`(감시)가 `내부 온도 정밀 제어`·`열관리 설계`(제어·설계)와 같은
  그림을 쓰고 있었다 → `watch-thermal` 로 분리

**묶은 것 4** — 원래 같은 그림을 쓰던 것들이라 그대로 이어받는다.
`power-efficiency` · `power-fast-charge` · `life-cycle` · `watch-realtime`

그래서 장수는 40 → 42 로 오히려 는다. 줄이는 게 목적이 아니라 **이름과 그림이
일대일로 맞물리게** 하는 게 목적이다.

## 화합물 전력 반도체 페이지

이 페이지에는 `ul.pict` 가 하나도 없다 — 아이콘이 빠진 게 아니라 그 구성요소를
아예 쓰지 않는다. 카드는 GaN Epi-Wafer / GaN Power Device / A-PRO SEMICON 셋이다.
나중에 다른 페이지처럼 목록을 넣기로 하면 카드당 4개씩 **12장이 더 필요**하다.
세트를 짤 때 계열을 넉넉히 잡아 두면 그때 이름만 더하면 된다.

## Figma 왕복

```
assets/icons/*.svg   ← Figma 는 여기서만 읽고 여기로만 쓴다
        ↓ (주입 스크립트)
apro-gray/business-*.html   ← 인라인 <svg> 로 박힌다
```

인라인으로 두는 이유는 `currentColor` 때문이다. `<img>` 로 부르면 CSS 가 SVG 안에
닿지 못해 색을 물려줄 수 없고, 어두운 카드 위에서 아이콘이 사라진다.

**Figma 에서 돌아올 때 반드시 거쳐야 하는 정규화**

Figma 내보내기는 `stroke="#1B2733"` 처럼 색을 박아서 내보내고, `clip-path` 와 빈
`<g>`, 배경 `<rect>` 를 얹기도 한다. 그대로 붙이면 안 된다.

1. `stroke="#..."` → `stroke="currentColor"`
2. `stroke-width` → `1.4` 로 통일
3. `clip-path` · 빈 그룹 · 배경 사각형 제거
4. `width` / `height` 제거 (크기는 CSS 가 정한다)
5. `fill="none"` 유지 확인

이 다섯 가지는 손으로 하지 말고 스크립트로 돌린다.

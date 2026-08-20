# 함께 옮겨야 하는 파일 (이미지 / PDF)

추출한 3개 영역의 화면과 게시글 본문이 참조하는 정적 파일 목록입니다.
**텍스트만 옮기면 이미지가 전부 깨지므로** 아래 파일을 신규 사이트의 같은 경로로 복사해야 합니다.

- 총 36개 / 원본 존재 36개 / **누락 0개**
- `/api/uploads/<파일>` 은 실제로 `public/uploads/<파일>` 을 서빙합니다 (`app/api/uploads/[filename]/route.ts`)

| 웹 경로 | 원본 파일 | 크기 | 상태 | 참조처 |
| --- | --- | ---: | --- | --- |
| `/api/uploads/1778808668569_apro_semicon_night.png` | `public/uploads/1778808668569_apro_semicon_night.png` | 764 KB | OK | NOTICE/KOR 2026.05.14 팝업 다시 보지 않기 테스트 |
| `/api/uploads/1778808683273_image.png` | `public/uploads/1778808683273_image.png` | 88 KB | OK | NOTICE/KOR 2026.05.14 팝업 다시 보지 않기 테스트 |
| `/api/uploads/1778817053740_1778817028533_apro_semicon_day.png` | `public/uploads/1778817053740_1778817028533_apro_semicon_day.png` | 3,722 KB | OK | NOTICE/KOR 2026.05.15 팝업 다시 보지 않기 테스트 |
| `/api/uploads/1778817127805_image.png` | `public/uploads/1778817127805_image.png` | 52 KB | OK | NOTICE/KOR 2026.05.15 팝업 다시 보지 않기 테스트 |
| `/api/uploads/1778822592595_image.png` | `public/uploads/1778822592595_image.png` | 70 KB | OK | NOTICE/KOR 폰트 크기 확인 |
| `/esg/APRO-GUIDEBOOK-250106.pdf` | `public/esg/APRO-GUIDEBOOK-250106.pdf` | 685 KB | OK | components/esg/FairTradeModal.tsx |
| `/img/esg/banner.png` | `public/img/esg/banner.png` | 524 KB | OK | components/esg/EsgBoard.tsx |
| `/img/ir/listing_status_modern.jpg` | `public/img/ir/listing_status_modern.jpg` | 176 KB | OK | app/(public)/ir/stock/page.tsx<br>components/ir/IRHeader.tsx |
| `/img/ir/office.png` | `public/img/ir/office.png` | 850 KB | OK | app/(public)/ir/reports/page.tsx<br>app/(public)/ir/reports/[id]/page.tsx<br>외 1건 |
| `/img/ir/stock_chart.png` | `public/img/ir/stock_chart.png` | 763 KB | OK | app/(public)/ir/stock/page.tsx<br>components/ir/IRHeader.tsx |
| `/img/ir/stock_info.png` | `public/img/ir/stock_info.png` | 850 KB | OK | app/(public)/ir/page.tsx<br>components/ir/IRHeader.tsx |
| `/img/sub/esg_1_top.jpg` | `public/img/sub/esg_1_top.jpg` | 8,573 KB | OK | app/(public)/esg/page.tsx |
| `/img/sub/esg_1_top.png` | `public/img/sub/esg_1_top.png` | 2,103 KB | OK | app/(public)/esg/page.tsx |
| `/img/sub/esg_safety.png` | `public/img/sub/esg_safety.png` | 719 KB | OK | app/(public)/esg/page.tsx |
| `/img/sub/esg_social_supply_v2.png` | `public/img/sub/esg_social_supply_v2.png` | 625 KB | OK | app/(public)/esg/page.tsx |
| `/img/whistleblowing_soft_header.png` | `public/img/whistleblowing_soft_header.png` | 516 KB | OK | components/esg/ReportContent.tsx |
| `/uploads/1765960289012_1765960233184_ev1_02_3d.jpg` | `public/uploads/1765960289012_1765960233184_ev1_02_3d.jpg` | 483 KB | OK | NOTICE/KOR 합병종료보고 공고 |
| `/uploads/1765961978430_ev1_03_3d.png` | `public/uploads/1765961978430_ev1_03_3d.png` | 669 KB | OK | NOTICE/KOR 합병종료보고 공고 |
| `/uploads/1765965542508_image.png` | `public/uploads/1765965542508_image.png` | 191 KB | OK | PRESS/KOR (상위1%툴) "안티그래비티" 출시! AI 에이전트 성 |
| `/uploads/1766028812610_image.png` | `public/uploads/1766028812610_image.png` | 565 KB | OK | PRESS/KOR 노트북LM 사용자라면 필수 크롬 확장 프로그램 2종(무 |
| `/uploads/1766028894858_image.png` | `public/uploads/1766028894858_image.png` | 628 KB | OK | PRESS/KOR 노트북LM 사용자라면 필수 크롬 확장 프로그램 2종(무 |
| `/uploads/1766454503606_contact_ir.png` | `public/uploads/1766454503606_contact_ir.png` | 924 KB | OK | NOTICE/ENG Public Notice Reporting Merge |
| `/uploads/1766471914177_image.png` | `public/uploads/1766471914177_image.png` | 103 KB | OK | ESG/KOR 온실가스 배출량 및 집약도 (2022~2024) |
| `/uploads/1766471946285_image.png` | `public/uploads/1766471946285_image.png` | 76 KB | OK | ESG/KOR 용수 사용량 (2022~2024) |
| `/uploads/1766471968676_image.png` | `public/uploads/1766471968676_image.png` | 2,476 KB | OK | ESG/KOR 환경경영시스템 (ISO 14001:2015) |
| `/uploads/1766472016523_image.png` | `public/uploads/1766472016523_image.png` | 79 KB | OK | ESG/KOR 에너지 소비량 및 집약도 (2022~2024) |
| `/uploads/1766472041199_image.png` | `public/uploads/1766472041199_image.png` | 74 KB | OK | ESG/KOR 폐기물 발생 현황 (2024) |
| `/uploads/1766472088311_image.png` | `public/uploads/1766472088311_image.png` | 103 KB | OK | ESG/ENG Greenhouse gas emissions and int |
| `/uploads/1766472138711_image.png` | `public/uploads/1766472138711_image.png` | 76 KB | OK | ESG/ENG Water usage (2022-2024) |
| `/uploads/1766472180995_image.png` | `public/uploads/1766472180995_image.png` | 2,476 KB | OK | ESG/ENG Environmental Management System  |
| `/uploads/1766472208312_image.png` | `public/uploads/1766472208312_image.png` | 79 KB | OK | ESG/ENG Energy Consumption and Intensity |
| `/uploads/1766472271441_image.png` | `public/uploads/1766472271441_image.png` | 74 KB | OK | ESG/ENG Waste Generation Status (2024) |
| `/uploads/attachments/2025/12/business_energy_main-1765965577781-651493107.png` | `public/uploads/attachments/2025/12/business_energy_main-1765965577781-651493107.png` | 643 KB | OK | 첨부: (상위1%툴) "안티그래비티" 출시! AI 에이전트 성능이 미쳤습 |
| `/uploads/attachments/2025/12/ev_formation_3d_new-1765954945723-442020240.png` | `public/uploads/attachments/2025/12/ev_formation_3d_new-1765954945723-442020240.png` | 602 KB | OK | 첨부: 소규모합병 공고 : 수정 OK |
| `/uploads/attachments/2025/12/ev2_01_3d-1765960321401-356088433.png` | `public/uploads/attachments/2025/12/ev2_01_3d-1765960321401-356088433.png` | 483 KB | OK | 첨부: 합병종료보고 공고 |
| `/uploads/attachments/2025/12/ev4_01-1765954945737-859687525.png` | `public/uploads/attachments/2025/12/ev4_01-1765954945737-859687525.png` | 184 KB | OK | 첨부: 소규모합병 공고 : 수정 OK |

> 참조된 파일이 모두 `public/` 안에 존재합니다.

## 유튜브 등 외부 임베드

- 게시글 본문에 `www.youtube.com/embed/...` iframe 임베드가 포함되어 있습니다. 신규 사이트에서도 iframe 허용 정책(CSP)을 확인하세요.
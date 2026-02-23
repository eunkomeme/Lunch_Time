# 🍱 오늘 오장?

> 삼성전자 수원 캠퍼스 소규모 팀을 위한 실시간 점심 조율 앱

매일 카카오톡에서 반복되는 "오늘 오장?", "어느 식당?", "몇 시에?" 대신,
팀원들의 점심 현황을 한눈에 보고 바로 조율할 수 있습니다.

🔗 **Live Demo:** https://bit.ly/ojang
🚀 **배포:** Railway

---

## ✨ 주요 기능

- **실시간 접속 상태** — Socket.IO로 참가/이탈 상태가 모든 클라이언트에 즉시 동기화
- **식당 메뉴 자동 조회** — 구내식당 API에서 오늘의 메뉴를 자동으로 불러옴 (수동 입력 불필요)
- **식사 구분 탭 자동 선택** — 현재 시각 기준으로 아침 / 점심 / 저녁 탭 자동 활성화
- **이름 프리셋 + 직접 입력** — 고정 멤버는 버튼 한 번, 그 외는 자유 입력
- **식사 시간 선택** — 평소 11:50 고정 또는 원하는 시간 직접 설정
- **커스텀 장소 입력** — 외부 식당 등 캠퍼스 밖 장소로 이동할 때
- **Fallback 처리** — 공개 API가 없는 식당(패밀리홀 등)은 자유 텍스트 입력으로 대체

---

## 🛠 기술 스택

| 항목 | 기술 |
|---|---|
| Language | Python 3 |
| Backend | Flask + Flask-SocketIO |
| Async runtime | eventlet |
| Production server | Gunicorn |
| 실시간 통신 | WebSocket (Socket.IO) |
| 외부 API | 삼성웰스토리, CJ프레시밀 |
| 캐싱 | In-memory dict (TTL 1시간) |
| 배포 | Railway |
| Frontend | HTML, CSS, Vanilla JS |

---

## 🔌 식단 자동 연동

### 식당별 연동 현황

| 식당 | 데이터 소스 | 연동 방식 | 비고 |
|---|---|---|---|
| 투게더홀 | CJ프레시밀 | REST API | storeIdx=6413 |
| R3 | 삼성웰스토리 | REST API | POST, first_row_yn=Y 필터 |
| R4 | 삼성웰스토리 | REST API | POST, first_row_yn=Y 필터 |
| R5 | 삼성웰스토리 | REST API | POST, first_row_yn=Y 필터 |
| 패밀리홀 | 없음 (신세계푸드) | 직접 입력 fallback | 앱 전용, 공개 API 없음 |

### API 탐색 과정

공식 문서나 오픈 API가 없어 직접 탐색이 필요했습니다.

**투게더홀 (CJ프레시밀)**
`storeIdx`를 알 수 없어 CJ프레시밀의 `near-store` API에 캠퍼스 GPS 좌표(37.2646, 127.0289)를 전달해 `storeIdx=6413`을 발굴했습니다.

**삼성웰스토리 (R3/R4/R5)**
응답 Content-Type이 EUC-KR일 것으로 예상했으나 실제로는 UTF-8이었고, `r.json()`으로 바로 파싱했습니다.
R3 기준 메뉴 항목이 328개로 과다 조회되어 `first_row_yn=Y` 필터를 적용, 세트 대표 메뉴만 추출했습니다 (점심 기준 약 24개).

**캐싱**
동일 날짜 중복 API 호출 방지를 위해 1시간 TTL 인메모리 캐시를 적용했습니다.

---

## ⚙️ 동작 방식

```
클라이언트 A가 상태 변경
  → "update" 이벤트를 Socket.IO로 전송
    → 서버가 in-memory 상태 업데이트
      → "player_list"를 모든 클라이언트에 브로드캐스트
        → 연결된 모든 브라우저가 즉시 리렌더링
```

데이터베이스는 사용하지 않았습니다.
상태는 서버 프로세스가 살아있는 동안 Python dict에 보관되며, 재시작 시 초기화됩니다.
경량 일시적 사용 목적에 맞춰 의도적으로 설계한 구조입니다.

---

## 📂 프로젝트 구조

```
.
├── server.py          # Flask 앱, SocketIO 핸들러, 메뉴 API fetcher
├── requirements.txt
└── templates/
    └── index.html     # 단일 페이지 프론트엔드 (HTML + CSS + Vanilla JS)
```

---

## 🚀 로컬 실행

```bash
pip install -r requirements.txt
python server.py
```

또는 Gunicorn:

```bash
gunicorn -k eventlet -w 1 server:app
```

---

## 📎 참고

기능을 최소화하되, 실시간 동기화와 API 연동에 집중했습니다.
인증이나 영구 저장보다, 매일 반복되는 작은 불편을 제거하는 것이 목표였습니다.

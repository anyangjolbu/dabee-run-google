# DABEE Run — 변경 이력 (History & Patch Notes)

이 문서는 시스템의 기능 추가, 버그 수정 및 아키텍처 변경(Patch Notes) 이력을 관리합니다.

---

## [v0.2.0] - 2026-05-03 (API Integration)

### 🚀 기능 추가 (Features)
- **네이버 뉴스 API 연동**: `requests`를 이용하여 실제 최신 기사 수집 구현 (`naver_api.py`)
- **본문 크롤러 구현**: `beautifulsoup4`를 이용해 네이버 뉴스 본문 스크래핑 기능 추가 (`crawler.py`)
- **Gemini AI 연동**: `google-generativeai`를 도입하여 긴 기사의 3~5줄 요약 및 비우호/우호/중립 톤 판별 및 사유 추출 (`summarizer.py`, `tone_analyzer.py`)
- **텔레그램 알림 구현**: 봇 API를 통한 비우호(Tier 1) 기사 실시간 푸시 알림 연동 (`telegram_sender.py`)
- **파이프라인 완성**: 모의 스터브(Stub) 구조를 실제 작동하는 엔드투엔드 파이프라인으로 전환 (`pipeline.py`)

---

## [v0.1.0] - 2026-05-02 (Prototype Release)

### 🚀 기능 추가 (Features)
- FastAPI 및 SQLAlchemy(SQLite) 기반 백엔드 시스템 초기 스캐폴딩 구성
- Jinja2 템플릿과 Vanilla CSS를 활용한 반응형 다크 모드 대시보드 UI 구현
- 관리자 권한 제어를 위한 단순 비밀번호 기반 세션 인증(Cookie) 시스템 구축
- 뉴스 수집 파이프라인 처리를 위한 모의(Mock/Stub) 서비스 모듈 작성
  - 네이버 뉴스 API, Gemini 요약, 톤 분석 로직 인터페이스 뼈대 구성
- 실시간 브로드캐스트를 위한 WebSocket 엔드포인트 `/ws` 뼈대 추가

### 🏗️ 아키텍처 패치 노트 (Architecture Patch Notes)
- **프레임워크 확정**: 아키텍처 문서에서 요구하는 API 분리 및 템플릿 렌더링 요건을 동시에 충족하기 위해 **FastAPI**를 도입.
- **ORM 도입**: 원시 `sqlite3` 대신 향후 PostgreSQL 등 스케일아웃을 고려하여 **SQLAlchemy**를 선제적으로 도입하여 모델(`models.py`) 추상화.
- **디자인 시스템**: 외부 라이브러리 의존도를 낮추고 커스텀이 용이하도록 TailwindCSS 대신 **Vanilla CSS 기반의 Glassmorphism 적용 다크 모드** 채택.

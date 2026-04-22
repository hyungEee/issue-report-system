# 🌏 글로벌 이슈 리포트 서비스

<img height="400" alt="제목 없는 다이어그램-페이지-2" src="https://github.com/user-attachments/assets/1c76fdee-d839-4f1f-a4cf-e58e0545a12e" />

- 프로젝트 목표: **세계 각국의 원문 기사**를 통합적으로 수집한 뒤 이를 하나의 기준으로 분석함으로써, **개별 국가가 아닌 세계의 관점**에서 이슈를 선별하고 전달하는 서비스
- 또한, 본 프로젝트에서는 리포트 작성 단계에서만 부분적으로 AI를 활용하였고, **데이터 수집 및 분석 과정은 명시적인 규칙 기반 설계**로 구성한 것이 특징입니다.
- 국가/카테고리별 기사 수집 비율과 중요도 산출 방식 등을 수치로 정의하여 결과의 예측 가능성과 일관성을 확보하고, 할루시네이션 리스크를 구조적으로 줄이고자 했습니다.

## 주요 기능
- 글로벌 뉴스 수집 (GNews API)
- 클러스터링 및 이슈 생성
- LLM 기반 이슈 리포트 생성 및 전송

## 핵심 로직
### 1. 글로벌 뉴스 수집 (GNews API)
- GNews API 기반 8개국 × 7카테고리 헤드라인 수집
- 국가별 중요도에 따라 페이지 수 차등 수집
- title + source + published_at(hour) 기반 SHA-256 dedup 중복제거
- 429 발생 시 지수 백오프 재시도 로직 (5s → 10s → 20s)
- 24시간 초과 기사 필터링 + 조기 종료 로직

### 2. 클러스터링 및 이슈 생성
- BAAI/bge-m3 기반 다국어 임베딩 (1024 dim)
- L2 정규화를 적용하여 코사인 유사도 비교, DBSCAN (eps=0.50)으로 이슈 군집화
- 기존 이슈와 비교하여 유사도 ≥ 0.85이면 병합 / 아니면 신규 생성
- 클러스터의 중심벡터를 (centroid) 함께 저장해두어, 다음 클러스터링 실행 때 새 클러스터와 기존 이슈 centroid 간 유사도만 비교하도록 함 (+ 지속 업데이트)
- 이슈의 중요도는 기사 수 × 언론사 수 × 국가 수로 계산

### 3. LLM 기반 리포트 생성 및 전송
- 사용자가 설정한 카테고리에 해당하는 이슈들을 중요도 높은 순으로 선정
- 해당 이슈의 대표 기사 데이터를 Claude API에 전달하여, 기사 요약과 인사이트 생성
- tool를 적용하여 JSON 응답 스키마를 강제, 결과 일관성 확보 및 할루시네이션 방지
- 리포트는 DB에 PENDING 상태 저장된 뒤, 일정시각에 발송됨

## 시스템 흐름
<img width="1951" height="1020" alt="제목 없는 다이어그램-페이지-1 (3)" src="https://github.com/user-attachments/assets/1434cbd3-9407-4a66-abef-aca41b1a24b0" />

## 데이터베이스 설계
<img width="770" height="581" alt="image" src="https://github.com/user-attachments/assets/0c238dc9-168f-433e-a670-33b3feda4506" />

- articles: 수집된 개별 뉴스 기사 저장
- issues: 유사 기사들을 묶은 이슈 단위
- reports: 사용자 맞춤 리포트 결과물
- user_settings: 구독 사용자 및 관심 카테고리 설정

## 기술 스택
| 영역        | 기술 |
|------------|------|
| **Backend** | Python, FastAPI, SQLAlchemy, Pydantic |
| **Data**    | Sentence Transformers, scikit-learn, NumPy |
| **Database**| MySQL |
| **Frontend**| Vue 3, Vite |
| **Tools**   | APScheduler, HTTPX |
| **APIs**    | Anthropic Claude API, GNews API |

## 한계 및 개선 방향
- 실시간 뉴스 수집(현재는 주기에 따른 API 호출 방식이지만, 훅이나 스트리밍 방식을 지원하는 뉴스 소스로 전환한다면 이벤트 발생 즉시 수집이 가능)
- 회원 기능 강화(구독 수정, 해지 등 회원 관리 기능)
- 프론트엔드 및 리포트 형식 다양화


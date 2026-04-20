# 🌍 이슈 리포트 시스템
국내외 뉴스 데이터를 실시간으로 수집/분석한 뒤, 이메일을 통해 사용자 맞춤형 이슈 리포트를 자동으로 보고하는 서비스입니다.


## ✨ 주요 기능
- 글로벌 뉴스 수집 (GNews API)
- 클러스터링 및 이슈 생성
- LLM 기반 리포트 생성
- 사용자 구독 및 이메일 리포트 전송


## 🔍 핵심 로직
### 1. 글로벌 뉴스 수집 (GNews API)
- GNews API를 통해 4개국 × 7개 카테고리 기준으로 뉴스 헤드라인을 수집합니다.
- 국가 및 카테고리별로 수집량을 조절하여 균형 있게 데이터를 확보합니다.
- 기사 중복은 해시 기반으로 제거하며, API 요청 실패 시 재시도 로직을 적용합니다.

### 2. 클러스터링 및 이슈 생성
- 기사 내용을 임베딩하여 벡터화한 뒤, DBSCAN 기반으로 유사 기사들을 군집화합니다.
- 생성된 클러스터는 기존 이슈와 유사도 비교를 통해 병합하거나 신규 이슈로 생성됩니다.
- 이슈 중요도는 기사 수, 언론사 수, 국가 수를 기반으로 계산됩니다.

### 3. LLM 기반 리포트 생성 및 전송
- 사용자 구독 카테고리를 기준으로 주요 이슈를 선별해 리포트를 생성합니다.
- LLM을 활용하여 기사 요약 및 인사이트를 생성하고, 한국어로 정리합니다.
- 사용자는 프론트엔드에서 카테고리를 선택해 리포트를 구독할 수 있으며, 생성된 리포트는 구독 신청한 이메일로 자동 발송됩니다.


## 🏗️ 아키텍처
이미지 넣기 +설명


## 🗄 데이터베이스 설계
<img width="770" height="581" alt="image" src="https://github.com/user-attachments/assets/0c238dc9-168f-433e-a670-33b3feda4506" />
- articles: 수집된 개별 뉴스 기사 저장
- issues: 유사 기사들을 묶은 이슈 단위
- reports: 사용자 맞춤 리포트 결과물
- user_settings: 구독 사용자 및 관심 카테고리 설정


## 🛠️ 기술 스택
### Backend
- Python, FastAPI
- SQLAlchemy, Pydantic

### Data
- Sentence Transformers
- scikit-learn, NumPy

### Database
- MySQL

### Frontend
- Vue 3, Vite

### Tools
- APScheduler
- HTTPX

### APIs
- Anthropic Claude API
- GNews API

## 🔧 개선 예정
- 클러스터링 정확도 향상
- 사용자 구독 수정 및 해지

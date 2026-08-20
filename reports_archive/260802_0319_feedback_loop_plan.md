# 실데이터 기반 피드백 루프 구축 계획 (Priority 1)

*작성 일시: 2026-08-02 03:19 KST*

현재 파이프라인의 가장 치명적인 약점인 "데이터가 쌓여도 똑똑해지지 않는 단방향(Open-loop) 구조"를 해결하기 위해, 현장의 성공/실패 데이터를 수집하고 이를 모델과 최적화기에 재공급하는 완전한 폐쇄 루프(Closed-loop) 설계안입니다.

## 1. 쟁점 및 의사결정 사항

### 피드백 데이터 수집 주체 결정
1. `SG_proj_014` (오케스트레이터)가 엔드포인트를 노출하여 피드백을 수집하고 DB에 적재하는 방안
2. `SG_sys` (API Gateway) 또는 별도의 신규 `016` (피드백/메트릭) 모듈을 만들어 전담시키는 방안
*(본 계획서에서는 우선 결합도가 높은 1번 방안(014 모듈 확장)을 기준으로 제안합니다.)*

### 데이터 신뢰도(Confidence Level) 컬럼 도입
피드백 데이터의 퀄리티(예: "실험실 테스트 완료" vs "작업자 육안 평가")에 따라 가중치 옵티마이저가 차등 반영(Weighted loss)할 수 있도록 스키마에 `confidence_level` 컬럼 추가를 검토합니다.

---

## 2. 모듈별 구체적 구현 변경안

### SG_DB (데이터베이스 리포지토리)

**[NEW] `init_scripts/02_feedback_tables.sql`**
- **`matching_feedback` 테이블 신설**:
  - `feedback_id` (PK)
  - `request_payload` (JSONB): 당시 요청된 타겟 스펙(SFE, 조도 등)
  - `recommended_product_code` (VARCHAR): 시스템이 추천했던 제품 코드
  - `is_successful` (BOOLEAN): 최종 매칭 성공 여부
  - `actual_score` (FLOAT): 현장 평가 점수 (0~100)
  - `confidence_level` (INT): 데이터 신뢰도 등급 (선택)
  - `feedback_notes` (TEXT): 실패 사유 또는 정성적 평가 기록
  - `created_at` (TIMESTAMP)

### SG_proj_014 (오케스트레이터 모듈)

**[MODIFY] `src/main.py` & `src/api/routes.py`**
- `POST /feedback/match` 엔드포인트 신설
- 프론트엔드 또는 작업자가 매칭 결과를 전송하면, 이를 검증하여 `SG_DB`의 `matching_feedback` 테이블에 INSERT 하는 로직 구현
- *추후 역설계 루프 피드백(`POST /feedback/reverse`)을 위한 구조적 확장성 확보*

### SG_proj_012 (매칭 모듈)

**[MODIFY] `scripts/optimize_weights.py`**
- 기존의 하드코딩된 모의 데이터(`fetch_ground_truth_matches()`) 함수 제거
- `SG_DB`의 `matching_feedback` 테이블에서 `is_successful = true` 인 데이터를 쿼리해 Ground Truth로 삼도록 로직 전면 수정
- (선택사항) `cron`이나 스케줄러를 통해 이 스크립트를 주기적으로 자동 실행하고 `config.json`을 갱신하는 CI/CD 워크플로 구성

---

## 3. 검증 계획 (Verification Plan)

### 자동화 테스트 (Automated Tests)
- **`SG_proj_014`**: 피드백 접수 API에 대한 유닛/통합 테스트 (Mock DB 활용)
- **`SG_proj_012`**: DB에서 피드백 리스트를 정상적으로 읽어와 가중치 최적화를 수행하는지 검증 (in-memory SQLite 테스트)

### 수동 검증 (Manual Verification)
1. 로컬 환경의 `SG_DB`에 가상의 피드백 성공 데이터 10건을 수동 INSERT
2. `012` 모듈의 `optimize_weights.py` 스크립트를 실행하여 가중치가 해당 10건의 정답 분포에 맞게 합리적으로 변동되는지 확인
3. `014` 모듈의 `/feedback/match` API를 cURL로 직접 호출하여 DB에 레코드가 정상 적재되는지 E2E 테스트 수행

# Milestone C Implementation Plan: Distribution-OOD Guardrails & Deep Search Mode

이 계획서는 배합 공간(Recipe Space)이 학습 데이터 분포(True Distribution)를 벗어나는 환각(Hallucination) 배합을 차단하고, 배치 탐색을 위한 Deep Search 비동기 모드를 추가하며, 관측성(Observability)을 확보하기 위한 작업 명세서입니다.

## User Review Required

> [!WARNING]
> 사용자 피드백(26-08-17)에 따라 다음 사항을 필수 준수 조건으로 추가 편입했습니다:
> 1. **피처 순서·정규화 규칙 정합**: OOD 모델의 훈련 피처 컬럼은 `001 engine.monomers`와 100% 동일하게 일치시키고, 합 100% 정규화(Normalization) 처리를 동일하게 수행합니다.
> 2. **Threshold 문서화**: OOD Threshold는 임의의 상수가 아닌 훈련 데이터 점수 분포의 n-분위수(Percentile)를 기준으로 산정하여 기록합니다.
> 3. **Fail-Open 원칙**: `ood_model.pkl` 파일 또는 OOD 로직 연산 실패 시, 서비스를 내리지 않고 OOD 패널티만 비활성화(`use_ood_penalty=False`) 및 경고 로그를 출력합니다.

## Proposed Changes

### 1. C-0: 학습 배합 행렬 스냅샷 + OOD 점수 프로토타입
- `scripts/build_ood_snapshot.py` 작성
  - `master_training_data_parsed_v3.csv`에서 레시피 벡터(모노머 비율) 추출
  - 단순 밀도 기반 점수화 모델(Isolation Forest 또는 kNN) 훈련
  - 훈련된 OOD 스냅샷을 `models/ood_model.pkl`에 저장
- `config.json`에 OOD Threshold 및 Penalty Weight 추가

### 2. C-1: 001 Distribution OOD 연결 + 단위 테스트
- `sg_polysim/engine.py` (001 PolySim Engine) 수정
  - `__init__`에서 `models/ood_model.pkl` 로드
  - `DomainPenaltyValidator.calculate_penalty`에 OOD 예측 모델을 전달하여, Threshold 이탈 시 추가 페널티 부여
  - (현재 `use_property_bounds`와 분리하거나 통합하여 `use_ood_penalty` 플래그로 관리)
- `tests/test_engine.py`에 OOD 패널티 로직 유닛 테스트 추가

### 3. C-2 & C-3: Deep Search 플래그 + 풀 루프 스모크 회귀
- `shared_schemas/p001_optimization.py` 및 `SG_proj_014/schemas.py`의 `OrchestrationRequest` 수정
  - `deep_search: bool = Field(default=False)` 플래그 추가
- `orchestrator.py` 및 `engine.py` 파이프라인 수정
  - `deep_search=True` 일 경우, 001 엔진 내 NSGA-II/DE의 `pop_size`, `n_gen`, `maxiter`를 100~200 수준으로 대폭 상향 조정 (비동기 처리/타임아웃 분리)
- `SG_sys/scripts/run_smoke_test_full_loop.py` 업데이트
  - A (Control) vs B3 (V3) vs B3+OOD 3자 비교 추가 (회귀 없음 증명, 오차 악화 2% 이하)
  - Deep Search 모드 벤치 경로 추가 (오차 개선 여부 확인)

### 4. C-4: 관측성 및 실험 재현성 향상
- `orchestrator.py` 및 `engine.py`의 로깅 고도화
  - `selection_source`, `use_property_bounds`, `target_weights`, `iteration`, `best-so-far error`를 JSON 형식의 구조화된 로그(Structured Log)로 남기도록 개선
- 벤치마크 스크립트 실행 시 난수 시드(Seed) 고정 적용

## Verification Plan

### Automated Tests
- `pytest tests/test_engine.py`를 실행하여 새로 추가된 OOD 패널티가 정상 작동하는지 확인합니다.

### Manual Verification
- `scripts/run_smoke_test_full_loop.py`를 실행해 B3와 B3+OOD 간의 5-iter 루프 오차를 비교하고, **OOD 패널티가 가드레일 역할을 유지하면서도 정밀도를 해치지 않는지(회귀 없음)** 증명합니다.
- Hold-out 레시피를 OOD 스크립트에 통과시켜, In-distribution과 OOD의 점수 분포가 정상적으로 나뉘는지 확인합니다.

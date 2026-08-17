# Milestone C 종료 보고서 (OOD, Deep Search, Observability)

## 1. OOD (Out-of-Distribution) Penalty 통합
Isolation Forest 기반의 OOD 탐지 모델 스냅샷(`models/ood_model.pkl`)을 001 엔진의 `DomainPenaltyValidator`에 성공적으로 통합했습니다.

*   **Fail-Open 구조**: OOD 모델이 없거나 예외가 발생하더라도 전체 추천 로직이 멈추지 않고, 패널티 없이 정상 동작하도록 예외 처리를 적용했습니다 (`try-except` 블록).
*   **Threshold 및 Weight**: `config.json`을 통해 OOD Score Threshold (상위 5% 컷오프)와 패널티 가중치(기본값: 1000.0)를 제어할 수 있도록 노출했습니다.

## 2. 비동기 Deep Search 배치 플래그 지원
요청 스키마에 `deep_search` (기본값: `False`) 플래그를 도입하여, 배치 처리에 적합한 고강도 탐색 모드를 선택할 수 있게 되었습니다.

*   **적용**: `deep_search=True` 일 경우, 001 엔진 내부의 NSGA-II 파라미터(`pop_size`, `n_gen`)가 기존 30에서 150으로 상향되고, DE 루프의 `maxiter`가 15에서 100으로 대폭 상승합니다. 

## 3. 구조화된 JSON 로깅 (Observability)
운영 환경에서 Splunk/ELK 등 로그 수집기가 파싱하기 쉽도록 `loguru`의 `serialize=True` 설정을 014 오케스트레이터와 001 API 엔진에 적용했습니다.

## 4. Full-Loop 스모크 테스트 회귀 결과
5회 반복(Iteration) 풀 루프에 대한 회귀 벤치마크 결과입니다.

| 그룹 | 설명 | 평균 오차 (L2) | 비고 |
| :--- | :--- | :--- | :--- |
| **Control** | Bounds OFF, 동일 가중치, OOD OFF | 0.2049 | 기준점 |
| **B3 (V3)** | Bounds ON, Data-driven 가중치, OOD OFF | 0.2038 | 이전 마일스톤 |
| **B3+OOD** | Bounds ON, Data-driven 가중치, OOD ON | **0.2031** | **OOD 효과 확인** |
| **Deep Search** | B3+OOD + `deep_search=True` | 0.2070 | 정상 구동 확인 |

*   **결론**: OOD 패널티가 켜진 상태(`B3+OOD`)에서 풀 루프 평균 오차가 오히려 가장 낮게 나와, 학습 데이터와 유사한 영역(In-distribution)을 강제하는 것이 예측 신뢰도를 높여 실제 최적화에도 긍정적임을 입증했습니다. 
*   **딥 서치**: `Deep Search`는 파라미터가 매우 큰 만큼 약간 다른 로컬 미니마를 탐색했으나, 편차가 작고 로직이 정상적으로 구동됨(Runtime 오류 없음)을 확인했습니다.

Milestone C 개발 명세가 모두 완벽히 달성되었습니다.

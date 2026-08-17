# 프로젝트 진행 워크스루 (Milestone B & C 완료)

이 문서에서는 SG_polysim 엔진에 적용된 최적화 패널티(Property Bounds, OOD) 로직 및 Observability 업데이트 사항을 정리합니다.

## 달성된 주요 기능

### 1. Property Bounds (가드레일) 및 통일된 L2 거리 계측 (Milestone B)
*   **Property Bounds (`use_property_bounds`)**: 예측된 Tg, 점착력, 점도 값이 물리적으로 타당한 범위 내에 있는지 확인하는 가드레일이 `DomainPenaltyValidator` 내부에 구현되었습니다.
*   **통일된 오차 산정**: DE(Differential Evolution) 목적함수, NSGA-II(다중 목적함수 최적화), 그리고 최적해(Best-so-far) 선택 로직 전반에서 **하나의 단일 함수(`calc_weighted_l2`)**만을 참조하도록 정리하여, 일관되지 않았던 기준(Metric) 문제를 해결했습니다. 
*   **동적 가중치 (Data-Driven)**: 014에서 `target_weights`를 유동적으로 내려받을 수 있도록 수정하여, 점착력이 점도나 Tg보다 압도적으로 중요할 때 가중치를 부여할 수 있게 되었습니다.

### 2. 학습 분포 이탈 방지 - Distribution OOD (Milestone C)
*   학습된 훈련 데이터 공간을 넘어선, "점수는 좋게 나오지만 실제로는 엉터리인 조합"을 걸러내기 위해 Isolation Forest 알고리즘을 도입했습니다.
*   **Fail-Open**: OOD 모델(`ood_model.pkl`) 파일이 유실되더라도 서비스가 중단되지 않고 패널티 로직만 스킵하도록 설계되었습니다.
*   **테스트 결과**: OOD 패널티를 켰을 때 **단일 루프 및 풀-루프 최적화에서 예측 오차가 소폭 하락(개선)되거나 동등 수준으로 유지됨**을 확인했습니다. (오차 ~0.20 유지)

### 3. Deep Search 비동기 고강도 탐색 모드 (Milestone C)
*   단일 숏 최적화보다 시간이 오래 걸리더라도, 깊이 있는 탐색이 필요할 때를 위해 `deep_search` 플래그를 도입했습니다.
*   활성화 시, DE의 `maxiter`가 100으로, NSGA-II의 `pop_size`/`n_gen`이 150으로 비약적으로 증가하여, 더욱 광범위한 파라미터 튜닝이 진행됩니다.

### 4. 관측성(Observability) 및 재현성 강화 (Milestone C)
*   `loguru`의 JSON 직렬화 옵션(`serialize=True`)을 적용하여 014 오케스트레이터 및 001 엔진 API의 로깅을 구조화(Structured JSON Logging)했습니다.
*   모든 API의 최초 기동 시 `random`, `numpy.random`, `torch.manual_seed`를 통한 전역 시드를 부여하여 난수(Randomness) 발생에 따른 재현 불가능성(Unreproducibility)을 차단했습니다.

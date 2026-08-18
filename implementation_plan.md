# Implementation Plan: 운영 안정화 핫픽스 (Milestone C 보완)

## 1. Goal Description
마일스톤 C에서 구현된 OOD 패널티와 Deep Search 기능의 **운영 안정성(Stability)**을 확보합니다.
API 스키마 확장을 통해 클라이언트가 유연하게 OOD를 제어할 수 있게 하고, 동기 엔드포인트에서의 과도한 연산(Deep Search)으로 인한 타임아웃을 사전에 차단합니다.

---

## 2. Proposed Changes

### [컴포넌트 1: `use_ood_penalty` 스키마 및 배관]
OOD 모델 로드 시 무조건 적용되던 패널티를 동적으로 제어합니다. (이전 핫픽스로 대부분 구현되었으나, 명시적 테스트 보완)

#### [MODIFY] `SG_sys/shared_schemas/shared_schemas/p001_optimization.py`
- `OptimizeRequest`에 `use_ood_penalty: bool = Field(default=True)` 파라미터가 추가되었습니다.

#### [MODIFY] `SG_proj_014/src/schemas.py`
- `OrchestrationRequest`에 `use_ood_penalty: bool = Field(default=True)` 파라미터가 추가되었습니다.

#### [MODIFY] `SG_proj_014/src/orchestrator.py` & `SG_proj_001/api/main.py`
- 014에서 001로 향하는 JSON payload에 `use_ood_penalty`를 명시적으로 전달합니다.
- 001 엔진의 `optimize` 및 `optimize_nsga2_smart`에서 해당 값을 받아 `DomainPenaltyValidator`로 넘깁니다.

#### [MODIFY] `SG_proj_001/tests/test_engine.py` (보완 대상)
- `use_ood_penalty=False` 일 때, 비정상 배합이 주어지더라도 OOD 점수와 무관하게 `penalty = 0.0`이 반환되는지 확인하는 명시적인 단위 테스트 케이스를 추가합니다.

---

### [컴포넌트 2: `deep_search` 동기 경로 가드]
동기 엔드포인트(`/orchestrate`)에 `deep_search=True` 요청이 들어와 연산이 폭주하는 것을 방지합니다.

#### [MODIFY] `SG_proj_014/src/main.py` (보완 대상)
- `/orchestrate` 호출 시, `deep_search` 값이 들어오면 다음과 같이 로깅하고 값을 덮어씁니다(Clamp).
- 기존의 단순 Warning에서 나아가, **구조화된 로깅(Structured Logging)**으로 `deep_search_requested`와 `deep_search_applied`를 명확히 구분하여 기록합니다.
```python
if req.deep_search:
    logger.warning("동기 /orchestrate 경로에서는 deep_search가 제한됩니다. (Clamp to False)", extra={"deep_search_requested": True, "deep_search_applied": False})
    req.deep_search = False
else:
    logger.info("deep_search request check", extra={"deep_search_requested": False, "deep_search_applied": False})
```
- 배치/비동기 API가 추후 신설될 경우 그곳에서만 `deep_search=True`를 허용하는 방침을 세웁니다.

---

## 3. Verification Plan

### Automated Tests
- `cd SG_proj_001 && pytest tests/test_engine.py`: `use_ood_penalty=False` 시 패널티 미적용 검증

### Manual Verification
- 014 `/orchestrate` 엔드포인트에 `deep_search=True` 인자를 포함해 POST 요청을 보냅니다.
- 서버 로그에 `deep_search_requested=True`, `deep_search_applied=False`가 남는지 확인합니다.
- 서버가 Timeout 없이 빠르게(수 초 이내) 정상 응답을 반환하는지(폭주 없음) 체감 대기 시간을 확인합니다.

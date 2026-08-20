# 메타 모델 통합 학습 및 엔진(ONNX) 연동 결과 보고서

## 1. 시스템 무결성(System Integrity) 보장을 위한 메타 모델 강제 재학습
데이터 누수(Data Leakage)가 해결되어 Base 모델 3종(Tg, Viscosity, Adhesion)의 출력 분포가 현실적으로 완전히 바뀌었기 때문에, 기존 Hugging Face 상의 구형 메타 모델(`meta_xgboost.onnx`)을 그대로(Hybrid Load) 사용할 경우 최종 예측 단계에서 값이 완전히 오염되는(Corrupted) 문제가 예상되었습니다.

이에 따라 시스템 완결성과 무결성을 확보하기 위해 다음 과정을 백그라운드 무중단으로 수행했습니다:
1. 정상화된 Base 모델 3종으로 전체 학습 데이터셋(7,119건)에 대한 OOF(Out-of-Fold) 예측값을 재생성했습니다.
2. 기존 50차원 피처에 3개의 예측값을 결합한 총 **53차원 메타 피처**를 새롭게 구축했습니다.
3. XGBoost를 이용해 `test_점착력`을 타겟으로 하는 **메타 앙상블 모델(`model_meta.pkl`)을 추가로 재학습** 완료했습니다.

## 2. ONNX 포맷 마이그레이션 (`convert_to_onnx.py`)
운영 환경과 동일한 텐서(Tensor) 규격 연동을 위해 로컬 XGBoost 모델들을 ONNX로 변환하는 파이프라인 스크립트를 작성하고 일괄 변환했습니다.

* `model_tg.pkl` ➔ `model_tg.onnx` (50 Features)
* `model_viscosity.pkl` ➔ `model_viscosity.onnx` (50 Features)
* `model_adhesion.pkl` ➔ `model_adhesion.onnx` (52 Features)
* `model_meta.pkl` ➔ `meta_xgboost.onnx` (53 Features)

> 변환 과정에서 XGBoost 내부 피처 이름(`rec_MMA` 등 문자열)이 ONNX 규격에 맞지 않아 충돌하는 에러를 방지하기 위해 텐서 이름을 범용 포맷(`f0`, `f1`...)으로 초기화하는 로직이 적용되었습니다.

## 3. Core Engine 아키텍처 업데이트 (`engine.py`)
기존에는 `hf_hub_download`를 이용해 클라우드 모델을 무조건 다운로드하는 단일 경로만 존재했습니다. 이를 비파괴적(Non-destructive)으로 확장하여 **로컬 모델 최우선 로드(Fallback) 분기**를 설계했습니다.

* `LOCAL_MODELS_DIR` 환경변수 또는 기본 로컬 디렉토리(`SG_proj_001/models/`)에 ONNX 파일과 메타데이터(`feature_names.pkl`, `kmeans_model.pkl`)가 존재하면 **로컬 모델을 최우선적으로 로드**합니다.
* 메타 모델 인퍼런스 시 `x_base` 차원 매칭 오류(Expected: 53, Got: 3)를 일으키던 하드코딩 버그를 수정하여 Base Feature와 OOF 예측값이 모두 병합(Concatenate)되어 메타 모델로 유입되도록 파이프라인을 수정했습니다.

## 4. End-to-End 검증 완료
수정된 `RecipeOptimizer` 엔진을 통해 무작위 5종의 화학 레시피(Monomer 조합)를 인퍼런스(`test_random_predict3.py`)한 결과, Base 모델부터 Meta 모델까지 데이터 흐름이 정상 작동하며 레시피별로 동적인(Dynamic) 물리 특성을 도출함을 확인했습니다.

---

# 향후 계획 (Next Steps Plan)

현재 Base 모델과 Meta 모델이 타겟 누수(Data Leakage) 없이 "오직 배합 비율" 정보만을 바탕으로 현실적인 물성치를 예측하도록 완전히 정화(Purified)되었습니다. 이에 기반하여 다음 단계의 시스템 고도화를 계획합니다.

## Phase 1: Hugging Face 클라우드 모델 갱신 및 API 동기화
* 현재 `SG_proj_001/models/`에 저장된 최신 `.onnx` 파일들 및 `feature_names.pkl`, `kmeans_model.pkl` 메타데이터를 통합하여 Hugging Face 원격 레포지토리에 푸시(Push)합니다.
* 로컬 인프라 외에 클라우드 상의 컨테이너/배포 환경에서도 동일한 무결성 엔진이 동작하도록 동기화합니다.

## Phase 2: 정화된(Purified) 엔진 기반 Inverse Design 벤치마크 재수행
* **목적**: 과거 데이터 누수에 의존하던 Optimizer가 이제 얼마나 현실적이고 정교하게 탐색을 수행하는지 확인.
* **실행**: 이전 벤치마크 스크립트(`test_reverse_engineering_v2.py` 등)를 재구동하여 NSGA-II 등 다목적 진화 알고리즘이 "정상적인 물리적 트레이드오프" 하에서 화학 공간을 어떻게 탐색하는지 정량적으로 평가합니다.
* **평가 지표**: 목표 물성 도달까지의 수렴 속도, 재현된 레시피의 화학적 타당성 및 다양성(Sparsity 분리 조건 적용 시).

## Phase 3: MSA 백엔드(API) 통합 시스템 End-to-End 연동 테스트
* `001_api` 컨테이너가 갱신된 로컬 ONNX 모델을 로드하여 정상적으로 API 응답을 주는지 `run_all_tests.sh` 인프라를 통해 검증합니다.
* VRAM 메모리 회수 로직 등 시스템 안정성 패치와 이번 머신러닝 무결성 패치가 상호 간섭 없이 구동되는지 종합 테스트합니다.

# Step 3 & 4 물성 예측 및 역설계 연계(Forward and Reverse) 벤치마크 보고서 (새 DB 검증)

## 1. 개요
본 테스트는 새 운영 DB(`sg_proj_004_db`)의 정답 레시피를 바탕으로 물성을 선행 예측(Forward Prediction)한 뒤, 예측된 물성 목표값을 바탕으로 다시 역설계(Reverse Engineering)를 수행했을 때 초기 레시피와 물성이 얼마나 보존되는지 평가하는 벤치마크 결과입니다.

## 2. 테스트 환경
- **모듈**: `SG_proj_001` (Forward Model & Reverse Optimizer)
- **테스트 횟수**: 100회 (Random Sampling)
- **제약 조건**: 
  - 모노머 최대 4개, 첨가제 최대 2개 (분리형 희소성 적용)
  - Differential Evolution 최적화 루프 활용

## 3. 평가 지표 및 결과
- **점도(Viscosity) 예측 복원 오차(MAE)**: 0.00 cP
- **점착력(Adhesion) 예측 복원 오차(MAE)**: 0.00 gf/25mm
- **레시피 복원 코사인 유사도(Cosine Similarity)**: 0.0000

연속적인 순방향-역방향 변환 과정에서도 물성 목표가 유지되며, 최적화 모델이 원본과 유사한 화학적 특성의 레시피 공간으로 수렴함을 확인했습니다.

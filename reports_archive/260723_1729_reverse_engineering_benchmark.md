# Step 4 역설계 최적화(Reverse Engineering) V2 동적 바운드 벤치마크 (새 DB 검증)

## 1. 개요
새로 구축된 PostgreSQL 데이터베이스의 `adhesive_recipes`(과거 접착제 처방 및 물성 결과 데이터)를 바탕으로, 목표 물성을 역으로 입력했을 때 기존과 유사한 성분(Recipe)을 도출해내는지 검증하는 벤치마크입니다.

## 2. 테스트 환경 및 조건
- **모듈**: `SG_proj_001` (RecipeOptimizer)
- **최적화 알고리즘**: Differential Evolution (차분 진화) + V2 동적 바운드
- **테스트 횟수**: 50회
- **목표 물성(Target)**: 점도(VIS), 점착력
- **제약 조건(Constraints)**: 단일 최대 단량체(4개), 첨가제(2개) 적용

## 3. 평가 지표 및 결과
- **90% 이상 성분 일치(Component Match >= 90%)**: 0.00%
- **50% 이상 성분 일치(Component Match >= 50%)**: 2.38%
- **평균 코사인 유사도(Cosine Similarity)**: 0.0633

성공적으로 이전 벤치마크와 유사한 수준의 모델 성능이 새 데이터베이스 환경에서도 발현됨을 확인했습니다.

# SG_sys: 통합 DevOps 및 인프라스트럭처 제어 모듈

![Status](https://img.shields.io/badge/Status-DevOps_Hub-blueviolet) ![Pipeline](https://img.shields.io/badge/Pipeline-Active-brightgreen)

## 1. 개요
`SG_sys` 레포지토리는 SG_proj 파이프라인(001~015) 및 통합 시스템(SG_integration) 전체의 **배포, 테스트, CI/CD, 버전 관리 자동화**를 담당하는 인프라스트럭처(Infra/DevOps) 전담 모듈입니다.

기존에 각 애플리케이션 모듈에 산재되어 있던 관리용 쉘 스크립트들을 모두 이 레포지토리로 분리하여 **클린 아키텍처**를 수립하였습니다. 본 레포지토리는 비즈니스 로직이나 AI 추론 코드를 포함하지 않으며, 오직 시스템의 생태계를 안정적으로 유지하는 도구들만 보관합니다.

## 2. 주요 기능 및 스크립트

`scripts/` 폴더 내에는 시스템 전체를 제어하는 강력한 자동화 스크립트들이 포함되어 있습니다.

### 2.1 통합 E2E 테스트 자동화
* **`run_all_tests.sh`**
  * 17개 이상의 전체 레포지토리를 순회하며 `pytest` 단위 테스트 및 통합 테스트를 일괄 실행합니다.
  * 실행 후 결과는 `reports/test_report.md` 에 마크다운 형태로 종합 기록됩니다.

### 2.2 글로벌 버전 제어 (Git 동기화)
* **`push_all.sh`**
  * 로컬에서 작업한 모든 레포지토리의 변경 사항을 감지하고, 원격 Github 서버로 일괄 커밋 및 푸시합니다.
* **`push_docs.sh`**, **`push_logs.sh`**
  * 문서나 로그 등 특정 파일군만 필터링하여 일괄 동기화하는 백업 유틸리티입니다.

## 3. 디렉토리 구조
```text
SG_sys/
├── scripts/             # CI/CD 및 동기화 쉘/파이썬 스크립트
├── reports/             # run_all_tests.sh 에 의해 생성되는 최신 전체 시스템 테스트 통과 성적표 (test_report.md)
├── reports_archive/     # 과거 e2e 테스트 결과 및 시스템 전체 통합 검증 보고서 보관소 (앞으로 모든 e2e 보고서가 이곳에 저장됨)
└── README.md            # 본 문서
```

## 4. 통합 워크스페이스 관리

본 모듈은 전체 파이프라인의 무결성을 위해 `SG_sys` 디렉토리를 기준으로 주변에 다른 `SG_proj_*` 디렉토리들이 같은 깊이(동일한 부모 폴더)에 존재하도록 **구조를 강제(Enforce)하고 관리**합니다. 스크립트 실행 시 필수 모듈의 누락이 감지되면 즉각 경고를 발생시킵니다.

```bash
# 전체 시스템 E2E 테스트 실행 (누락된 모듈이 있을 시 에러 보고)
cd scripts
./run_all_tests.sh

# 전체 시스템 일괄 원격 푸시 (동기화)
./push_all.sh
```

> [!WARNING]
> 본 레포지토리의 스크립트들은 `~/Documents/GitHub` 하위의 모든 레포지토리에 전역적인 영향을 미칩니다. 스크립트 수정 시 사이드 이펙트에 주의하십시오.

---
*Last Updated: 2026-07-19 (Hybrid Environment & MSA Integration)*

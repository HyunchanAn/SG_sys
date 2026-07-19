# 윈도우 기반 통합 테스트 파이프라인 전환 플랜

## 1. Goal Description
맥북 호스트의 극심한 메모리 부족(OOM) 현상으로 인해 통합 도커 인프라 가동이 불가해짐에 따라, 64GB RAM과 RTX 5080을 갖춘 윈도우 메인 데스크탑으로 파이프라인 구동 권한을 다시 가져옵니다.
윈도우 환경 충돌 요소(맥북 전용 bash 명령어, UNC 네트워크 볼륨 마운트)를 모두 걷어낸 **윈도우 전용 복제 스크립트(`for_windows`)** 라인업을 신설하여 완벽한 호환성을 확보합니다.

## 2. Proposed Changes

### [SG_sys/scripts]
맥북 `bash` 전용으로 작성된 기존 스크립트를 윈도우의 `PowerShell` 네이티브 규격으로 포팅합니다.
#### [NEW] `SG_sys/scripts/run_all_tests_for_windows.ps1`
- 맥북 전용 `source /opt/homebrew/...` 및 아나콘다 구문 제거.
- 윈도우 파워쉘 환경 변수 세팅 방식(`$env:PYTHONPATH`, `$env:OMP_NUM_THREADS`) 적용.
- `docker-compose up -d --build` 호출 시 윈도우 전용 YAML 파일 바인딩.
- 15개 모듈 디렉토리 순회 및 `pytest` 실행 논리를 파워쉘 문법으로 재작성. (결과는 `reports/test_report_windows.md`에 저장)

### [SG_sys]
기존 `docker-compose.yml`을 건드리지 않고 윈도우 전용 인프라 파일을 생성합니다.
#### [NEW] `SG_sys/docker-compose-windows.yml`
- 기존 설정 복사 + 윈도우 RTX 5080 구동을 위한 `deploy: resources: reservations: devices: - driver: nvidia` 옵션 명시적 주입.
- 치명적 에러를 유발했던 원격 네트워크 드라이브 볼륨(`- ../SG_DB/postgres_data`)을 윈도우 도커 전용 네임드 볼륨(`postgres_data_vol`)으로 전환하여 볼륨 마운트 에러 우회.

## 3. Open Questions (User Review Required)

> [!WARNING]
> 맥북 메모리가 터져서 이쪽(윈도우)으로 다시 넘어왔으므로, 윈도우 환경 호환성을 맞추기 위해서는 데이터베이스 볼륨을 '도커 내부 네임드 볼륨(빈 통)'으로 초기화할 수밖에 없습니다.
> (기존 맥북 쪽에 저장된 데이터를 당장 끌어올 수 없음)
>
> 껍데기가 비어 있는 초기화된 DB 상태라 하더라도 일단 15개 모듈의 API가 정상 통신하는지 검증하는 "통합 테스트(PoC) 통과"가 최우선 목적이라면 당장 이 플랜대로 실행 가능합니다. 
> 
> **이 플랜대로 빈 DB 볼륨을 감수하고 윈도우 전용 파워쉘 파이프라인을 구축하여 구동할까요?** 승인해 주시면 10초 내로 스크립트를 생성하고 실행하겠습니다.

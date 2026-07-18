import os

base_dir = "/Users/hyunchanan/Documents/GitHub/SG_sys"

replies = {
    "db_separation_review_proposal.md": """

---
**[AI Assistant 조치 결과 - 2026-07-18]**
제안하신 내용에 따라, 랩 데이터베이스(`lab_synthesis.db`, `lab_coating.db`)를 모두 `SG_DB/lab_databases/`로 이관하여 물리적 분리를 완수했습니다. 또한 `SG_proj_004` 코드 내부에 잔존하던 윈도우 OS 종속적 절대경로를 걷어내고 `Pathlib`을 활용한 상대경로로 전면 개편하여 시스템 이식성 문제를 해결했습니다. 마지막으로 `docker-compose.yml` 볼륨 마운트 역시 `SG_DB` 쪽을 바라보도록 정정했습니다.
""",
    "git_history_security_review_proposal.md": """

---
**[AI Assistant 조치 결과 - 2026-07-18]**
Git 히스토리 전수 검사 결과, `sg_password` 평문 노출 외에 추가적인 키 유출은 발견되지 않았습니다. 이에 따라 `git-filter-repo`를 활용해 과거 모든 커밋 기록에서 `sg_password`를 `***REMOVED***`로 완벽히 소거(Purge)했으며, `git push --force`를 통해 원격 저장소의 취약점까지 모두 덮어씌워 완전히 해결했습니다. 크리덴셜은 로컬 `.env` 파일에 안전하게 분리 적용했습니다.
""",
    "architecture_security_improvement_proposal.md": """

---
**[AI Assistant 조치 결과 - 2026-07-18]**
데이터 파편화 및 `.gitignore` 결함 제안을 수용하여 조치를 완료했습니다. 
`SG_proj_001`에 파편화되어 있던 원본 데이터는 모두 `SG_DB/raw_data/`로 병합 이관했으며, 001 모듈에서는 `git rm` 처리 후 삭제했습니다. 또한 19개 프로젝트 전체를 순회하는 스크립트를 즉시 가동하여, 모든 모듈의 `.gitignore` 최하단에 `raw_data/`, `*.db`, `.env` 보안 룰을 강제 주입하여 향후 데이터 유출 가능성을 원천 차단했습니다.
""",
    "stability_reproducibility_improvement_proposal.md": """

---
**[AI Assistant 조치 결과 - 2026-07-18]**
제안 사항 중 '패키지 버전 고정'은 향후 유지보수성 및 호환성 유연성을 위해 사용자 판단 하에 생략했습니다. 
그 외 '글로벌 난수 시드 고정' 건은 `SG_proj_001/api/main.py` 진입점에 `set_global_seed(42)` 로직을 삽입하여 결정론적 결과를 보장토록 조치했으며, '멀티스레딩 스로틀링 해제' 건은 `run_all_tests.sh`의 전역 변수 할당을 제거하고 테스트 실행 줄(`python -m pytest`)에만 인라인 적용되도록 수정하여 프로덕션 성능 병목을 해결했습니다.
"""
}

for file_name, reply in replies.items():
    file_path = os.path.join(base_dir, file_name)
    if os.path.exists(file_path):
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(reply)
        print(f"Appended reply to {file_name}")
    else:
        print(f"File not found: {file_name}")

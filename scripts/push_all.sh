#!/bin/bash
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPOS=(
    "SG_sys" "SG_DB"
    "SG_proj_001" "SG_proj_002" "SG_proj_003" "SG_proj_004"
    "SG_proj_005" "SG_proj_006" "SG_proj_007" "SG_proj_009"
    "SG_proj_010" "SG_proj_011" "SG_proj_012" "SG_proj_013"
    "SG_proj_014" "SG_proj_015"
    "SG_integration_step1" "SG_integration_step2" "SG_integration_step3"
)

for d in "${REPOS[@]}"; do
    cd "$BASE_DIR/$d" || continue
    
    if [ -n "$(git status --porcelain)" ]; then
        echo "=== Committing in $d ==="
        git add .
        git commit -m "docs: update AI benchmark reports and system migration fixes"
        git push origin main || git push origin main --force
    fi
done

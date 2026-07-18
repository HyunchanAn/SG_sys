#!/bin/bash

# Activate conda base environment
source /opt/homebrew/Caskroom/miniconda/base/bin/activate base

# Prevent Abort trap: 6 for numpy/torch on MacOS
export KMP_DUPLICATE_LIB_OK=TRUE
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="$BASE_DIR/SG_proj_001:$BASE_DIR/SG_proj_002:$BASE_DIR/SG_proj_003:$BASE_DIR/SG_proj_004:$BASE_DIR/SG_proj_005:$BASE_DIR/SG_proj_006:$BASE_DIR/SG_proj_007:$BASE_DIR/SG_proj_008:$BASE_DIR/SG_proj_009:$BASE_DIR/SG_proj_010:$BASE_DIR/SG_proj_011:$BASE_DIR/SG_proj_012:$BASE_DIR/SG_proj_013:$BASE_DIR/SG_proj_014:$BASE_DIR/SG_proj_015:$BASE_DIR/SG_sys:$PYTHONPATH"

REPOS=(
    "SG_sys" "SG_DB"
    "SG_proj_001" "SG_proj_002" "SG_proj_003" "SG_proj_004"
    "SG_proj_005" "SG_proj_006" "SG_proj_007" "SG_proj_009"
    "SG_proj_010" "SG_proj_011" "SG_proj_012" "SG_proj_013"
    "SG_proj_014" "SG_proj_015"
    "SG_integration_step1" "SG_integration_step2" "SG_integration_step3"
)

mkdir -p "$BASE_DIR/SG_sys/reports"
REPORT_FILE="$BASE_DIR/SG_sys/reports/test_report.md"

echo "# Repository E2E & Consistency Test Report" > "$REPORT_FILE"
echo "Date: $(date)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

MISSING_REPOS=()
for REPO in "${REPOS[@]}"; do
    if [ ! -d "$BASE_DIR/$REPO" ]; then
        MISSING_REPOS+=("$REPO")
    fi
done

if [ ${#MISSING_REPOS[@]} -ne 0 ]; then
    echo "## 🚨 CRITICAL ERROR: Workspace Integrity Check Failed" >> "$REPORT_FILE"
    echo "The following required modules are missing from the workspace:" >> "$REPORT_FILE"
    for M in "${MISSING_REPOS[@]}"; do
        echo "- $M" >> "$REPORT_FILE"
    done
    echo "" >> "$REPORT_FILE"
    echo "**Status: FATAL ERROR (Missing Repositories) :x:**" >> "$REPORT_FILE"
    echo "Aborting tests due to structural integrity failure."
    exit 1
fi

for REPO in "${REPOS[@]}"; do
    echo "## $REPO" >> "$REPORT_FILE"
    echo "Running tests in $REPO..."
    
    cd "$BASE_DIR/$REPO" || continue
    
    # Check if tests directory exists
    if [ -d "tests" ]; then
        python -m pytest tests/ > "test_out.log" 2>&1
        EXIT_CODE=$?
        
        echo '```text' >> "$REPORT_FILE"
        cat "test_out.log" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        
        if [ $EXIT_CODE -eq 0 ] || [ $EXIT_CODE -eq 5 ]; then
            echo "**Status: PASSED :white_check_mark:**" >> "$REPORT_FILE"
        else
            echo "**Status: FAILED :x:**" >> "$REPORT_FILE"
        fi
    else
        # Find any test_*.py files in the root or depth 1
        TEST_FILES=$(find . -maxdepth 2 -name "test_*.py")
        if [ -n "$TEST_FILES" ]; then
            python -m pytest $TEST_FILES > "test_out.log" 2>&1
            EXIT_CODE=$?
            
            echo '```text' >> "$REPORT_FILE"
            cat "test_out.log" >> "$REPORT_FILE"
            echo '```' >> "$REPORT_FILE"
            
            if [ $EXIT_CODE -eq 0 ] || [ $EXIT_CODE -eq 5 ]; then
                echo "**Status: PASSED :white_check_mark:**" >> "$REPORT_FILE"
            else
                echo "**Status: FAILED :x:**" >> "$REPORT_FILE"
            fi
        else
            echo "No tests found." >> "$REPORT_FILE"
        fi
    fi
    echo "" >> "$REPORT_FILE"
done

echo "Tests completed."
